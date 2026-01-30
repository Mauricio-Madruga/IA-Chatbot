# Product Overview

## Project Purpose
Intelligent chatbot assistant for customer product inquiries using Amazon Bedrock Knowledge Base. The system provides accurate product specifications and pricing information by querying PDF documents stored in S3, optimized for production use with cost-effective Claude 3 Haiku model.

## Value Proposition
- **Accurate Information Retrieval**: Queries product catalog PDFs via Bedrock Knowledge Base for factual responses
- **Cost-Optimized**: Uses Claude 3 Haiku (~$0.0002 USD per query, ~$6 USD/month for 1000 daily queries)
- **Intelligent Query Classification**: Automatically detects query types (pricing, comparison, recommendations, specs)
- **Production-Ready**: Fixed model configuration, token limits, and optimized retrieval strategies

## Key Features

### Intelligent Query System
- **Automatic Classification**: Detects 6 query types (pricing, comparisons, superlatives, specs, recommendations, accessories)
- **Optimized Retrieval**: Adjusts chunk quantity based on query complexity
- **Specialized Prompts**: Generates type-specific instructions for accurate responses
- **Price Validation**: Verifies mentioned prices exist in retrieved context
- **Smart Re-ranking**: Prioritizes chunks with critical information (prices, specifications)

### Supported Query Types
1. **Specific Pricing**: "cuanto cuesta el iPhone 14 Pro?"
2. **Comparisons**: "cuál es más barato, iPhone 13 o Samsung A54?"
3. **Superlatives**: "cuál es el teléfono más barato?", "mejor cámara"
4. **Specifications**: "cuánta RAM tiene?", "duración de batería?"
5. **Recommendations**: "qué me recomiendas para gaming?"
6. **Accessories**: "fundas para iPhone 15?", "cargadores rápidos?"

### Production Optimizations
- **Fixed Model**: Claude 3 Haiku (most economical)
- **Always-On Knowledge Base**: Automatic PDF consultation from S3
- **Token Limits**: 500 tokens max per response (cost control)
- **Simplified Interface**: No unnecessary client options
- **Welcome Message**: Guides users from start

## Target Users
- **End Customers**: Consulting product specifications and prices
- **Sales Teams**: Quick access to accurate product information
- **E-commerce Platforms**: Automated customer support for product catalogs

## Use Cases
- Product specification lookups
- Price comparisons between models
- Product recommendations based on use case (gaming, photography, basic use)
- Accessory compatibility queries
- Technical specification verification
- Promotional offer information

## Cost Estimates
- Per query: ~$0.0002 USD
- Monthly (1000 queries/day): ~$6 USD
- Knowledge Base storage: ~$0.05/month
