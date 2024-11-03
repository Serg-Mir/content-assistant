# Content Assistant API - README

## Overview

The Content Assistant API is a REST API service designed to generate fluent English text based on various input parameters. The API can generate or enhance text by leveraging a collection of customer-provided texts, using these to improve the quality and relevance of generated content. This README explains how to set up, run, and use the application, as well as details the design and considerations taken to ensure production readiness.

## Features

- **Input Parameters**: Accepts a range of parameters including:
  - **Keywords or Seed Sentence**: The main topic for content generation.
  - **Domain/Vertical**: Specifies the domain (e.g., legal, advertising, e-commerce).
  - **Word Count**: Defines the length of the generated text.
  - **Target Audience**: Customizes the tone for the intended audience (e.g., scientist vs. consumer).
  - **Tone of Voice**: Specifies the tone of the generated text (e.g., formal, informal, playful).

- **Database Integration**: Looks up similar content in a database to enhance generated text quality.
- **Text Generation**: Uses a pre-trained model to generate fluent English text considering the given parameters.
- **UTF-16 Output**: Returns the generated text in UTF-16 format, encoded in Base64.

## Setup & Installation

### Prerequisites

- **Python 3.11** or newer.
- **Docker** and **Docker Compose** for containerization.

### Installation Steps

1. **Clone the Repository**:
   ```bash
   git clone git@github.com:Serg-Mir/content-assistant.git
   cd content-assistant
   ```

2. **Create Environment File**:
   Create a `.env` file in the root directory with the required environment variables(pre-defined .env file provided):
   ```env
   DATABASE_URL=postgresql://<username>:<password>@<host>:<port>/<database>
   UVICORN_HOST=0.0.0.0
   UVICORN_PORT=8000
   DEBUG=True
   ````

3. **Install Dependencies**:
   - Install all dependencies using `pip`:
     ```bash
     pip install -r requirements/requirements.txt
     ```

4. **Run Docker Compose**:
   - To set up the entire infrastructure (including the database, API server, and other services):
     ```bash
     docker-compose up --build
     ```

## Running the API

- **Local Environment**: You can run the API locally using Uvicorn.
  ```bash
  uvicorn content_assistant.main:app --host 0.0.0.0 --port 8000 --reload
  ```

- **Dockerized Environment**: To start the application with Docker Compose, run:
  ```bash
  docker-compose up
  ```

## Scaling with Docker Compose
* **Container Replicas**: The number of container replicas for the API service can be modified in the docker-compose.yml file to enhance scalability and handle more concurrent requests. To change the number of replicas, locate relevant section in the docker-compose.yml and adjust the replicas value:
```yaml
services:
  content_assistant:
    image: content_assistant:latest
    deploy:
      replicas: 3  # Adjust the number of replicas as needed
```
Increasing the number of replicas will allow the service to handle more requests simultaneously, improving resilience and scalability. Ensure that your infrastructure can support the additional load when increasing replicas.

## API Endpoints

- `POST /generate-text`: Generates text based on the input parameters.
- `GET /health`: Checks the health of the API.

### Example Request

```http
POST /generate-text
Content-Type: application/json

{
  "keywords": ["bread", "milk"],
  "domain": "e-commerce",
  "word_count": 10,
  "audience": "consumer",
  "tone": "playful"
}
```

### Example Response
The response contains the generated text encoded in UTF-16 Base64.

```json
{
  "generated_text": "<base64_encoded_text>"
}
```
Note: generated text can be seen in the application log, e.g.: 
```bash
app_1  | [2024-11-03 18:36:22,232] INFO [content_assistant_app]: Generated text saved to database: A woman is preparing a salad for dinner.
```
## Evaluation & Quality

- **Quality Evaluation**: The generated text can be evaluated based on content coherence, grammatical correctness, and relevance to the given parameters.
  - **Human Evaluation**: Subjective evaluation by domain experts.
  - **Automated Scoring**: Metrics like BLEU or ROUGE can be used for scoring fluency and relevance.

- **Optimization Strategies**:
  - **Inference Speed**: Optimize the model by using quantization and batch processing techniques.
  - **Scalability**: Add language support and use distributed model inference to handle high traffic.

## Scaling and Performance Optimization

- **Model Scaling**: To add new parameters or support additional languages, consider retraining the model with a diverse dataset.
- **Auto-Scaling**: Use Kubernetes or cloud services like AWS Fargate to auto-scale the service based on traffic.

- **Technical Considerations**:
  - **Security**: Implement authentication (e.g., OAuth2) to secure endpoints.
  - **Latency**: Cache results for frequently requested inputs to reduce response time.
  - **Concurrency**: Support concurrent requests using Kubernetes Horizontal Pod Autoscaler (HPA).
  - **GDPR Compliance**: Store data only in EU-based data centers to comply with GDPR requirements.

## Deployment

- **Local Deployment**: The Docker Compose setup allows for running the entire service locally.
- **Cloud Deployment**: The API can be deployed to a Kubernetes cluster on GCP, AWS, or Azure using Helm charts for efficient scalability.

## Operations Planning

- **SecDevOps Principles**: Ensure secure CI/CD pipelines with proper testing (unit, integration, security) before deployments.
- **Monitoring**: Use tools like Prometheus and Grafana for monitoring, and ELK stack for logging.
- **Cost Management**: Leverage cloud-native features like serverless or managed Kubernetes to optimize operational costs.

## Conceptual & Technical Design

### Conceptual Design
- **Input Handling**: Validate input parameters, and provide default options for certain fields (e.g., tone).
- **Text Enhancement**: Enhance generated content quality using customer-provided texts as reference material.
- **Output Processing**: Ensure generated text is UTF-16 encoded to meet output requirements.

### Technical Design
- **Data Flow**:
  1. Accept user input through API.
  2. Check database for similar content using FAISS.
  3. Generate or enhance content using a text generation model.
  4. Return the final text encoded in UTF-16.

- **Tools & Technologies**:
  - **API Framework**: FastAPI for creating REST APIs.
  - **Model Serving**: Pre-trained transformer model (`flan-t5-base`) via `transformers`.
  - **Database**: PostgreSQL for storing reference texts.
  - **Containerization**: Docker for packaging and deployment.

## Strategic Roadmap

1. **Short-Term Goals**:
   - Improve the model inference speed by using GPU instances.
   - Enhance the FAISS-based similarity search with advanced indexing.

2. **Mid-Term Goals**:
   - Add multi-language support for text generation.
   - Implement additional content-enhancement techniques like style transfer.

3. **Long-Term Goals**:
   - Develop a feedback loop with users to iteratively improve the content quality.
   - Expand infrastructure to handle hundreds of concurrent requests while maintaining low latency.

## Security & Compliance
- **GDPR Compliance**: All user data is processed and stored within the EU.
- **Data Security**: Data encryption both in transit (HTTPS) and at rest (database encryption).

## Production Considerations

- **Latency and Concurrency**: Implement rate limiting and API gateway to handle high loads.
- **Auto-Scaling**: Set up Kubernetes Horizontal Pod Autoscaler (HPA) to auto-scale the pods.

## How to Contribute
Contributions are welcome! Please create a pull request or open an issue on GitHub if you find a bug or have a suggestion for improvement.

## License

© 2024 Sergii Miroshnykov. All rights reserved.

This software is proprietary and may not be copied, modified, or distributed without the express permission of the copyright holder, Sergii Miroshnykov.
