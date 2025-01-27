# V. Three Please - Your Educational AI Companion

An Alexa skill that lets you chat with DeepSeek, an AI friend who provides clear, educational explanations in a friendly American male voice.

## Features

- Clear, educational explanations of any topic
- Friendly American male voice (Matthew)
- Uses DeepSeek Reasoner (R1) model for accurate responses
- Natural conversation style
- Comprehensive error handling and monitoring
- CloudWatch metrics and logging

## Usage

Just say:
- "Alexa, ask v. three please what is quantum computing"
- "Alexa, ask v. three please to explain black holes"
- "Alexa, ask v. three please about artificial intelligence"

## Monitoring and Debugging

### CloudWatch Metrics

All metrics are logged under the namespace `AlexaSkills/VThreePlease`:

1. **Usage Metrics**
   - `LaunchCount` - Number of skill launches
   - `AskCount` - Number of questions asked
   - `HelpCount` - Number of help requests
   - `StopCount` - Number of explicit stops
   - `SessionEndedCount` - Number of session ends

2. **Performance Metrics**
   - `APIResponseTime` (Seconds) - Time taken for DeepSeek API responses
   - `PromptLength` - Length of user prompts
   - `ResponseLength` - Length of AI responses

3. **Error Metrics**
   - `APIError` - Count of API-related errors
   - `ProcessingError` - Count of general processing errors
   - `UnhandledError` - Count of unhandled exceptions

### CloudWatch Logs

The skill logs detailed information for debugging:

1. **Request Logs**
   - Skill invocation details
   - User prompts
   - Intent handling

2. **Response Logs**
   - API responses (truncated for privacy)
   - Error details
   - Processing steps

### Monitoring Dashboard

To create a CloudWatch dashboard:

1. Go to AWS CloudWatch Console
2. Create a new dashboard named "VThreePlease"
3. Add widgets for key metrics:
   ```
   # Usage Overview
   SELECT SUM(LaunchCount), SUM(AskCount), SUM(HelpCount)
   FROM "AlexaSkills/VThreePlease"
   GROUP BY 1h

   # Error Rates
   SELECT SUM(APIError), SUM(ProcessingError), SUM(UnhandledError)
   FROM "AlexaSkills/VThreePlease"
   GROUP BY 1h

   # Performance
   SELECT AVG(APIResponseTime)
   FROM "AlexaSkills/VThreePlease"
   GROUP BY 1m
   ```

### Alerts and Notifications

Set up CloudWatch Alarms for:

1. Error Rate Thresholds
   ```
   Metric: SUM(APIError + ProcessingError + UnhandledError)
   Period: 5 minutes
   Threshold: > 5
   ```

2. API Response Time
   ```
   Metric: AVG(APIResponseTime)
   Period: 5 minutes
   Threshold: > 3 seconds
   ```

3. Usage Anomalies
   ```
   Metric: SUM(AskCount)
   Period: 1 hour
   Anomaly Detection: 2 standard deviations
   ```

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
   - Name: "V. Three Please"
   - Choose "Custom" model
   - Choose "Alexa-Hosted (Python)"
   - Click "Import skill"
   - Enter this repository's .git URL

2. Set Environment Variable:
   - Key: `DEEPSEEK_API_KEY`
   - Value: Your DeepSeek API key (get it from [DeepSeek Platform](https://platform.deepseek.com/api_keys))

## Development

This skill is designed to be hosted on Alexa-hosted skills, which provides:
- Free SSL certificate
- AWS Lambda function
- CloudWatch logs and metrics
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
   export DEEPSEEK_API_KEY=your_key_here
   ```
4. Run tests:
   ```bash
   python -m unittest test_lambda_function.py
   ```

## Security Notes

- Never commit your DeepSeek API key
- Use AWS Lambda environment variables
- Regularly rotate your API key
- Monitor credit usage
- Review CloudWatch logs for suspicious activity
- Set up CloudWatch alarms for security events

## License

Apache-2.0
