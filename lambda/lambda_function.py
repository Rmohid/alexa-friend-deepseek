#!/usr/bin/env python3

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
import requests
import json
import os
import sys
from datetime import datetime, timedelta

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return handler_input.request_envelope.request.type == "LaunchRequest"

    def handle(self, handler_input):
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
        return handler_input.request_envelope.request.type == "IntentRequest" and \
               handler_input.request_envelope.request.intent.name == "AskIntent"

    def format_response(self, text):
        """Format response with SSML voice"""
        return f'<speak><voice name="Joanna">{text}</voice></speak>'

    def handle(self, handler_input):
        try:
            # Get the prompt from the slot value
            slots = handler_input.request_envelope.request.intent.slots
            prompt = slots["prompt"].value

            # Get API key from environment
            api_key = os.environ.get('OPENROUTER_API_KEY')
            if not api_key:
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
                'HTTP-Referer': 'http://localhost:3000',
            }

            data = {
                'model': "deepseek-ai/deepseek-v3",
                'messages': [{'role': 'user', 'content': prompt}]
            }

            # Make API request
            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers=headers,
                json=data
            )
            
            # Check for credit-related errors
            if response.status_code == 402 or response.status_code == 429:
                error_data = response.json()
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

        except Exception as e:
            speak_output = self.format_response(
                "I'm having trouble thinking right now. Could you try asking me again?"
            )
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask("What would you like to know?")
                    .response
            )

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return handler_input.request_envelope.request.type == "IntentRequest" and \
               handler_input.request_envelope.request.intent.name == "AMAZON.HelpIntent"

    def handle(self, handler_input):
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
        return handler_input.request_envelope.request.type == "IntentRequest" and \
               (handler_input.request_envelope.request.intent.name == "AMAZON.CancelIntent" or
                handler_input.request_envelope.request.intent.name == "AMAZON.StopIntent")

    def handle(self, handler_input):
        speak_output = "Goodbye! I enjoyed our chat. Come back anytime you want to learn something new!"
        
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
handler = sb.lambda_handler()