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
- **Docker** version 20.10.0 or newer and **Docker Compose** version 1.29.0 or newer for containerization.
- **Cloud Provider Account** (optional): Required if deploying to cloud.

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
   - Install all dependencies using `pip` to run locally:
     ```bash
     pip install -r requirements/requirements.txt
     pip install -r requirements/requirements-torch.txt
     ```

4. **Run Docker Compose**:
   - To automatically set up the entire infrastructure including the database, API server, and other services(advised):
     ```bash
     docker-compose up --build
     ```

## Running the API

- **Local Environment**: You can run the API locally using Uvicorn.
  ```bash
  uvicorn content_assistant.main:app --host 0.0.0.0 --port 8000 --reload
  ```

- **Dockerized Environment**: To start the application with Docker Compose(advised), run:
  ```bash
  docker-compose up
  ```
### Flow
A typical Docker Compose workflow for this project includes the following containers:
- **content_assistant_db**: PostgreSQL database initialized with credentials defined in the `.env` file.
- **content_assistant_migrations**: Applies the latest migrations to the database using `alembic upgrade head`.
- **content_assistant_nginx**: Nginx container used to centralize and load balance requests between multiple app replicas.
- **app_{replicas}**: Application container instances, scaled to handle increased demand.

> ⚠️ **Note**: During the initial build of the application, the process might be slow as it involves downloading large model files from external repositories (e.g., Hugging Face). This includes pre-trained model weights and configurations, which can significantly impact build times depending on your network speed. Please allow sufficient time for the downloads to complete successfully. You will see logs related to model downloading, like tokenizer, vocab, and safetensors, during this phase.



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
  "keywords": ["human", "salad"],
  "domain": "e-commerce",
  "word_count": 10,
  "audience": "consumer",
  "tone": "informal"
}
```

### Example Response
The response contains the generated text encoded in UTF-16 Base64.

```json
{
  "generated_text": "<base64_encoded_text>"
}
```
Note: generated text can be found in the application log, e.g.:
```text
app_1  | [2024-11-03 18:36:22,232] INFO [content_assistant_app]: Generated text saved to database: A woman is preparing a salad for dinner.
```

# Further App Improvements Notes and Comments:

## Evaluation & Quality

- **Quality Evaluation**:
  - **Human Evaluation**: Domain experts assess the coherence, grammar, and relevance of the generated content. This provides qualitative feedback that ensures the generated text meets industry standards and user expectations.
  - **Automated Scoring**: Metrics like BLEU or ROUGE could be used for scoring fluency and relevance. BLEU scores can compare the generated text to reference examples, while ROUGE can evaluate the overlap of n-grams between the generated and reference texts, ensuring a quantitative measure of content quality. For example, BLEU scores can be used to compare generated text with reference texts to evaluate how well the model is performing.

- **Optimization Strategies**:
  - **Inference Speed**: Apply quantization and batch processing to improve response time. Quantization helps by reducing the model's precision without significantly affecting quality, thus speeding up inference.
  - **Scalability**: Expand language support and implement distributed model inference to handle higher traffic. This ensures the service is accessible to a wider audience while maintaining efficiency during peak usage times.

## Scaling & Deployment Considerations

- **Model Scaling**: Retrain the model using diverse datasets to support new parameters and additional languages. For instance, expanding the training dataset with multi-domain and multilingual texts can significantly enhance the model's versatility and accuracy across different content scenarios.
- **Auto-Scaling**: Use Kubernetes or AWS Fargate for automated scaling based on traffic demands. This ensures that the infrastructure can grow dynamically with user requests, preventing downtime and maintaining consistent service quality.
- **Auto-Scaling**: Use Kubernetes or AWS Fargate for automated scaling based on traffic demands.

### Deployment Options

- **Local Deployment**: Run locally using Docker Compose to set up infrastructure(implemented).
- **Cloud Deployment**: Deploy to Kubernetes clusters (GCP, AWS, Azure) for better scalability, using tools like Helm charts(not implemented).

### Technical Considerations
- **Security**: Use OAuth2 for authentication to protect API endpoints. Implement rate limiting to prevent abuse and ensure that sensitive data is securely managed.
- **Latency Reduction**: Implement caching for frequently requested inputs. Leveraging tools like Redis can reduce repeated computations, thereby improving response times for common requests.
- **Concurrency & Scalability**: Use Kubernetes HPA to automatically handle increased loads. Horizontal scaling enables handling multiple simultaneous requests without degrading performance.
- **GDPR Compliance**: Ensure all data is processed and stored in EU-based data centers. Additionally, maintain an audit trail for data usage and access to meet GDPR requirements.
- **Latency Reduction**: Implement caching for frequently requested inputs.
- **Concurrency & Scalability**: Use Kubernetes HPA or Cloud Solutions to automatically handle increased loads.
- **GDPR Compliance**: Ensure all data is processed and stored in EU-based data centers.

## Operations Planning

- **SecDevOps Principles**: Secure CI/CD pipelines with unit, integration, and security testing before deployments. Ensure secrets management is handled securely, such as using tools like HashiCorp Vault to store sensitive credentials and API keys.
- **Monitoring & Logging**: Use Prometheus and Grafana for metrics and ELK stack for comprehensive logging. Alerts should be configured for key metrics (e.g., response time, error rates) to quickly address any production issues.
- **Cost Management**: Opt for cloud-native solutions like serverless or managed Kubernetes to reduce operational costs. Continuously monitor and optimize resource usage to keep infrastructure costs under control while maintaining performance.
- **Monitoring & Logging**: Use Prometheus and Grafana for metrics and ELK stack for comprehensive logging.
- **Cost Management**: Opt for cloud-native solutions like serverless or managed Kubernetes to reduce operational costs.

## Conceptual & Technical Design

### Conceptual Design
- **Input Handling**: Validate input parameters and provide default values for certain fields.
- **Text Enhancement**: Leverage customer-provided texts to improve generated content.
- **Output Format**: Ensure the generated text is encoded in UTF-16 for compliance with requirements.

### App Technical Design
- **Data Flow**:
  1. Accepts user input via the API.
  2. Querying the database for similar content using FAISS.
  3. Generates or enhances content with a text generation model.
  4. Returns the output encoded in UTF-16.

- **Tools & Technologies**:
  - **API Framework**: FastAPI for building REST APIs.
  - **Text Generation**: Pre-trained transformer models (`flan-t5-base`) via `transformers`.
  - **Database**: PostgreSQL for storing reference texts.
  - **Containerization**: Docker for deployment packaging.

## Strategic Roadmap

1. **Short-Term**:
   - Use GPU instances to improve inference speed, reducing the response time for generating content. This will make the service more responsive, particularly during high-demand periods.
   - Optimize FAISS similarity search with more advanced indexing to ensure faster and more accurate retrieval of similar texts, which directly enhances the quality of generated content. Consider techniques such as HNSW (Hierarchical Navigable Small World) for improving search performance.

2. **Mid-Term**:
   - Add multi-language support(model change?) to make the API accessible to a broader audience.
   - Develop content-enhancement techniques like style transfer, allowing users to adapt generated texts to specific writing styles or voices.

3. **Long-Term**:
   - Introduce a feedback mechanism to continuously improve content and service quality. For example, integrate feedback forms to gather insights and use this data to fine-tune the model.
   - Scale the infrastructure to handle hundreds of concurrent requests while maintaining low latency, using autoscaling policies and server optimizations.

## Security & Compliance
- **Data Residency**: Store data in EU-based data centers to comply with GDPR.
- **Data Security**: Ensure all API endpoints are accessible only via HTTPS to protect data in transit. Use TLS for database connections and consider field-level encryption for sensitive information to further enhance data protection.

## Production Considerations

- **Latency & Concurrency**: Implement rate limiting and use an API gateway to manage high loads.
- **Auto-Scaling**: Set up Kubernetes Horizontal Pod Autoscaler (HPA) for dynamic scaling based on demand.

## Contributing

Before starting to contribute, please install `pre-commit` to ensure your changes are checked for style and standards before committing them to the repository:

    $ pre-commit install

[pre-commit](https://pre-commit.com) is installed automatically in development environment by pip.
If you are running the Docker setup, please install it with `pip` in your host machine:

    $ pip install pre-commit


## License

© 2024 Sergii Miroshnykov. All rights reserved.

This software is proprietary and may not be copied, modified, or distributed without the express permission of the copyright holder, Sergii Miroshnykov.
