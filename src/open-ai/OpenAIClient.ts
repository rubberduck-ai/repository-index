import axios from "axios";
import { Schema } from "zod";
import { OpenAIEmbeddingSchema } from "./OpenAIEmbedding";

export class OpenAIClient {
  private readonly apiKey: string;

  constructor({ apiKey }: { apiKey: string }) {
    this.apiKey = apiKey;
  }

  private async postToApi<T>({
    path,
    content,
    schema,
  }: {
    path: string;
    content: unknown;
    schema: Schema<T>;
  }): Promise<T> {
    try {
      const response = await axios.post(
        `https://api.openai.com${path}`,
        content,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${this.apiKey}`,
          },
        }
      );

      return schema.parse(response.data);
    } catch (error) {
      console.error(error);
      throw error;
    }
  }

  async generateEmbedding({ input }: { input: string }): Promise<{
    embedding: number[];
    usage: {
      model: string;
      totalTokens: number;
      promptTokens: number;
    };
  }> {
    const result = await this.postToApi({
      path: "/v1/embeddings",
      content: {
        model: "text-embedding-ada-002",
        input,
      },
      schema: OpenAIEmbeddingSchema,
    });

    return {
      embedding: result.data[0].embedding,
      usage: {
        model: result.model,
        totalTokens: result.usage.total_tokens,
        promptTokens: result.usage.prompt_tokens,
      },
    };
  }
}
