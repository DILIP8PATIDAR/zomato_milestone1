# Context: AI-Powered Restaurant Recommendation System (Zomato Use Case)

## Problem Statement

You are tasked with building an AI-powered restaurant recommendation service inspired by Zomato. The system should intelligently suggest restaurants based on user preferences by combining structured data with a Large Language Model (LLM).

---

## Objective

Design and implement an application that:

- Takes user preferences (such as location, budget, cuisine, and ratings)
- Uses a real-world dataset of restaurants
- Leverages an LLM to generate personalized, human-like recommendations
- Displays clear and useful results to the user

---

## System Workflow

### 1. Data Ingestion
- Load and preprocess the Zomato dataset from Hugging Face:
  [ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)
- Extract relevant fields such as:
  - Restaurant name
  - Location
  - Cuisine
  - Cost
  - Rating
  - etc.

### 2. User Input
Collect user preferences:
- **Location** (e.g., Delhi, Bangalore)
- **Budget** (low, medium, high)
- **Cuisine** (e.g., Italian, Chinese)
- **Minimum rating**
- **Additional preferences** (e.g., family-friendly, quick service)

### 3. Integration Layer
- Filter and prepare relevant restaurant data based on user input
- Pass structured results into an LLM prompt
- Design a prompt that helps the LLM reason and rank options

### 4. Recommendation Engine
Use the LLM to:
- Rank restaurants
- Provide explanations (why each recommendation fits)
- Optionally summarize choices

### 5. Output Display
Present top recommendations in a user-friendly format:
| Field | Description |
|---|---|
| **Restaurant Name** | Name of the restaurant |
| **Cuisine** | Type of cuisine served |
| **Rating** | Customer rating |
| **Estimated Cost** | Approximate cost for two |
| **AI-generated Explanation** | Why this restaurant fits the user's preferences |

---

## Architecture Overview

```
User Input
    │
    ▼
┌─────────────────────────┐
│   Input Collection UI   │  ← Location, Budget, Cuisine, Rating, Prefs
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  Data Ingestion Layer   │  ← Hugging Face Zomato Dataset
│  (Filter & Preprocess)  │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  Integration Layer      │  ← Structured data → LLM Prompt
│  (Prompt Engineering)   │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  LLM (Gemini / OpenAI)  │  ← Ranking + Explanation
│  Recommendation Engine  │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  Output Display         │  ← Top N Restaurants with AI explanations
└─────────────────────────┘
```

---

## Key Technical Components

| Component | Description |
|---|---|
| **Dataset** | [Zomato Restaurant Dataset on Hugging Face](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation) |
| **LLM** | Used for reasoning, ranking, and generating natural language explanations |
| **Filtering Logic** | Rule-based pre-filtering by location, budget, cuisine, rating |
| **Prompt Design** | Structured prompt injecting filtered restaurant data + user preferences |
| **Output Format** | Human-readable recommendation cards with AI-generated justifications |

---

## Source

Generated from: `problemStatement.txt`
Date: 2026-06-22
