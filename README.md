# Friend DeepSeek - Your Educational AI Companion

An Alexa skill that lets you chat with DeepSeek, an AI friend who provides clear, educational explanations in a friendly American female voice.

## Features

- Clear, educational explanations of any topic
- Friendly American female voice (Joanna)
- Uses DeepSeek V3 model for accurate responses
- Natural conversation style
- Comprehensive error handling
- Credit usage monitoring

## Usage

Just say:
- "Alexa, ask friend deepseek what is quantum computing"
- "Alexa, ask friend deepseek to explain black holes"
- "Alexa, ask friend deepseek about artificial intelligence"

## Skill Structure

This repository follows the Alexa-hosted skills package format:

```
.
├── lambda/
│   ├── lambda_function.py
│   └── requirements.txt
│
└── skill-package/
    ├── interactionModels/
    │   └── custom/
    │       └── en-US.json
    └── skill.json
```

## Setup Instructions

1. Create a new Alexa-hosted skill:
   - Go to [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask)
   - Click "Create Skill"
   - Name: "Friend DeepSeek"
   - Choose "Custom" model
   - Choose "Alexa-Hosted (Python)"
   - Click "Import skill"
   - Enter this repository's .git URL

2. Set Environment Variable:
   - Key: `OPENROUTER_API_KEY`
   - Value: Your OpenRouter API key

## Development

This skill is designed to be hosted on Alexa-hosted skills, which provides:
- Free SSL certificate
- AWS Lambda function
- CloudWatch logs
- Auto-scaling

### Local Testing

1. Clone this repository
2. Install dependencies:
   ```bash
   cd lambda
   pip install -r requirements.txt
   ```
3. Set environment variables:
   ```bash
   export OPENROUTER_API_KEY=your_key_here
   ```
4. Run tests:
   ```bash
   python -m unittest test_lambda_function.py
   ```

## Security Notes

- Never commit your OpenRouter API key
- Use AWS Lambda environment variables
- Regularly rotate your API key
- Monitor credit usage

## Error Handling

The skill provides clear feedback for different scenarios:

1. API Key Issues:
   - "I apologize, but I need to be properly configured first. Please contact the skill administrator."

2. Credit-Related Errors:
   - "I apologize, but we've run out of API credits. Please contact the skill administrator to add more credits."

3. General Errors:
   - "I'm having trouble thinking right now. Could you try asking me again?"

## Part of the AI Friends Series

This skill is part of a series of AI friend skills:
- Friend DeepSeek (this skill) - Educational explanations
- [Friend Grok](https://github.com/Rmohid/alexa-friend-grok) - Simple, fun explanations
- [Friend GPT](https://github.com/Rmohid/alexa-friend-gpt) - Sophisticated insights

## License

MIT License