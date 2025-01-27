#!/usr/bin/env python3

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
import requests
import json
import os
import sys
import time
import logging
import traceback
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize X-Ray safely
try:
    from aws_xray_sdk.core import patch_all, xray_recorder
    patch_all()
    XRAY_ENABLED = True
except Exception as e:
    logger.warning(f"X-Ray initialization failed: {str(e)}")
    XRAY_ENABLED = False

def safe_begin_subsegment(name):
    """Safely begin an X-Ray subsegment"""
    if XRAY_ENABLED:
        try:
            return xray_recorder.begin_subsegment(name)
        except Exception as e:
            logger.warning(f"Failed to begin subsegment {name}: {str(e)}")
    return None

def safe_end_subsegment():
    """Safely end an X-Ray subsegment"""
    if XRAY_ENABLED:
        try:
            xray_recorder.end_subsegment()
        except Exception as e:
            logger.warning(f"Failed to end subsegment: {str(e)}")

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # Add debug logging
        request = handler_input.request_envelope.request
        logger.info(f"LaunchRequestHandler - Request object type: {type(request)}")
        logger.info(f"LaunchRequestHandler - Request object dir: {dir(request)}")
        return handler_input.request_envelope.request.object_type == "LaunchRequest"

    def handle(self, handler_input):
        logger.info("Handling LaunchRequest")
        speak_output = ("Hi! I'm your DeepSeek friend, ready to help you understand anything. "
                       "What would you like to learn about? "
                       "Just ask me any question!")
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("What would you like to know?")
                .response
        )

class AskDeepseekIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # Add debug logging
        request = handler_input.request_envelope.request
        logger.info(f"AskDeepseekIntentHandler - Request object type: {type(request)}")
        logger.info(f"AskDeepseekIntentHandler - Request object dir: {dir(request)}")
        return handler_input.request_envelope.request.object_type == "IntentRequest" and \
               handler_input.request_envelope.request.intent.name == "AskIntent"

    def format_response(self, text):
        """Format response with SSML voice"""
        return f'<speak><voice name="Joanna">{text}</voice></speak>'

    def handle(self, handler_input):
        subsegment = None
        try:
            request_id = handler_input.request_envelope.request.request_id
            logger.info(f"Processing AskIntent request. RequestId: {request_id}")
            
            # Get the prompt from the slot value
            slots = handler_input.request_envelope.request.intent.slots
            prompt = slots["prompt"].value
            logger.info(f"Received prompt: {prompt}")

            # Get API key from environment
            api_key = os.environ.get('OPENROUTER_API_KEY')
            if not api_key:
                logger.error("OPENROUTER_API_KEY environment variable not set")
                return (
                    handler_input.response_builder
                        .speak(self.format_response(
                            "I apologize, but I need to be properly configured first. Please contact the skill administrator."
                        ))
                        .response
                )

            # Prepare API request
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://github.com/Rmohid/alexa-friend-deepseek',
                'X-Title': 'Alexa DeepSeek Friend'
            }

            data = {
                'model': 'deepseek/deepseek-r1',
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are a helpful AI assistant that provides clear, concise answers suitable for voice interaction.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'temperature': 0.7,
                'max_tokens': 150
            }

            # Make API request with timing
            start_time = time.time()
            subsegment = safe_begin_subsegment('openrouter_api_call')
            if subsegment:
                subsegment.put_annotation('prompt', prompt)
            
            logger.info(f"Making API request to OpenRouter. RequestId: {request_id}")
            logger.info(f"Request data: {json.dumps(data)}")
            
            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=10  # Add timeout to prevent hanging
            )
            
            api_duration = time.time() - start_time
            logger.info(f"API call completed in {api_duration:.2f} seconds. Status: {response.status_code}")
            logger.info(f"API response: {response.text}")
            
            if subsegment:
                subsegment.put_metadata('response_time', api_duration)
                subsegment.put_metadata('status_code', response.status_code)
            
            # Check for credit-related errors
            if response.status_code == 402 or response.status_code == 429:
                error_data = response.json()
                logger.error(f"API error response: {error_data}")
                if any(keyword in str(error_data).lower() for keyword in ['credit', 'quota', 'payment', 'billing']):
                    return (
                        handler_input.response_builder
                            .speak(self.format_response(
                                "I apologize, but I'm unable to help right now. Please try again later."
                            ))
                            .response
                    )
            
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            response_text = result['choices'][0]['message']['content']
            logger.info(f"Received API response. Length: {len(response_text)} chars")

            # Format response for Alexa with appropriate voice and follow-up
            speak_output = self.format_response(
                f"{response_text} Is there anything else you'd like to know?"
            )
            
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask("What else would you like to learn about?")
                    .response
            )

        except requests.exceptions.Timeout:
            logger.error("API request timed out")
            return (
                handler_input.response_builder
                    .speak(self.format_response(
                        "I'm sorry, but the request took too long. Please try asking again."
                    ))
                    .ask("What would you like to know?")
                    .response
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return (
                handler_input.response_builder
                    .speak(self.format_response(
                        "I'm having trouble connecting right now. Please try again in a moment."
                    ))
                    .ask("What would you like to know?")
                    .response
            )
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return (
                handler_input.response_builder
                    .speak(self.format_response(
                        "I'm having trouble thinking right now. Could you try asking me again?"
                    ))
                    .ask("What would you like to know?")
                    .response
            )
        finally:
            if subsegment:
                safe_end_subsegment()

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # Add debug logging
        request = handler_input.request_envelope.request
        logger.info(f"HelpIntentHandler - Request object type: {type(request)}")
        logger.info(f"HelpIntentHandler - Request object dir: {dir(request)}")
        return handler_input.request_envelope.request.object_type == "IntentRequest" and \
               handler_input.request_envelope.request.intent.name == "AMAZON.HelpIntent"

    def handle(self, handler_input):
        logger.info("Handling HelpIntent")
        speak_output = ("I'm your DeepSeek friend, an AI that loves to explain complex topics. "
                       "You can ask me anything you're curious about, from science to history to technology. "
                       "For example, try asking 'what is quantum computing?' or "
                       "'explain how black holes work'. What would you like to learn about?")
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("What would you like to know?")
                .response
        )

class CancelAndStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # Add debug logging
        request = handler_input.request_envelope.request
        logger.info(f"CancelAndStopIntentHandler - Request object type: {type(request)}")
        logger.info(f"CancelAndStopIntentHandler - Request object dir: {dir(request)}")
        return handler_input.request_envelope.request.object_type == "IntentRequest" and \
               (handler_input.request_envelope.request.intent.name == "AMAZON.CancelIntent" or
                handler_input.request_envelope.request.intent.name == "AMAZON.StopIntent")

    def handle(self, handler_input):
        logger.info("Handling CancelIntent or StopIntent")
        speak_output = "Goodbye! I enjoyed our chat. Come back anytime you want to learn something new!"
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # Add debug logging
        request = handler_input.request_envelope.request
        logger.info(f"SessionEndedRequestHandler - Request object type: {type(request)}")
        logger.info(f"SessionEndedRequestHandler - Request object dir: {dir(request)}")
        return handler_input.request_envelope.request.object_type == "SessionEndedRequest"

    def handle(self, handler_input):
        # Any cleanup logic goes here
        logger.info("Handling SessionEndedRequest")
        return handler_input.response_builder.response

class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.error(f"Uncaught exception: {str(exception)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        speak_output = ("I'm sorry, but something went wrong. "
                       "Please try again in a moment.")
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

# Build the skill
sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(AskDeepseekIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelAndStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())  # Add the session ended handler
sb.add_exception_handler(CatchAllExceptionHandler())

# Export the handler
lambda_handler = sb.lambda_handler()