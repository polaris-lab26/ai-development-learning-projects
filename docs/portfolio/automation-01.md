Automation 01 – Customer Sign-up Workflow

Business Problem

The project demonstrates how a customer sign-up process can be automated to reduce manual data entry, improve record-keeping and provide timely email notifications.

Solution and Architecture

The workflow was developed in Make using three connected modules:

1.  Custom Webhook – receives customer sign-up information.
2.  Google Sheets – Add a Row – records the submitted information.
3.  Microsoft 365 Outlook – Send an Email – sends an email notification.

The modules form a sequential workflow, transferring information between the connected services.

Implementation and Testing

The scenario, named Integration webhooks, was configured and saved in Make.

Testing was carried out using synthetic customer information. A successful execution was recorded in Make’s execution history, demonstrating that the workflow ran successfully.

The accompanying screenshot provides supporting evidence of the execution.

Failure Considerations and Limitations

The workflow relies on the availability and correct configuration of the webhook and connected third-party services. Potential issues include invalid input, failed module execution, duplicate submissions and interruptions to external services.

The use of synthetic information avoids exposing genuine customer data during testing. Any practical deployment would require appropriate access controls and consideration of personal-data handling.

The recorded successful execution demonstrates the tested workflow. It does not establish that every possible failure or duplicate scenario has been independently tested.

AI Assistance

No AI-generated handler code was required for this Make scenario. The workflow was configured using Make’s visual automation modules.

Supporting Evidence

-   Week 4 Portfolio Evidence – Full Report (PDF)
-   Make Successful Execution Screenshot
