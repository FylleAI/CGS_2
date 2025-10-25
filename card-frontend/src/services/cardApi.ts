/**
 * Card Service API Client
 */

import axios, { AxiosInstance } from 'axios';
import { API_CONFIG, CARD_ENDPOINTS } from '../config/api';
import type {
  BaseCard,
  CardRelationship,
  CreateCardRequest,
  UpdateCardRequest,
  CreateRelationshipRequest,
} from '../types/card';

class CardApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_CONFIG.BASE_URL,
      timeout: API_CONFIG.TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Get tenant ID from URL or localStorage
   */
  private getTenantId(): string {
    const params = new URLSearchParams(window.location.search);
    return params.get('tenant_id') || localStorage.getItem('tenant_id') || '';
  }

  /**
   * List all cards for tenant
   */
  async listCards(): Promise<BaseCard[]> {
    const tenantId = this.getTenantId();
    const response = await this.client.get<BaseCard[]>(CARD_ENDPOINTS.LIST, {
      params: { tenant_id: tenantId },
    });
    return response.data;
  }

  /**
   * Get single card by ID
   */
  async getCard(cardId: string): Promise<BaseCard> {
    const tenantId = this.getTenantId();
    const response = await this.client.get<BaseCard>(CARD_ENDPOINTS.GET(cardId), {
      params: { tenant_id: tenantId },
    });
    return response.data;
  }

  /**
   * Create new card
   */
  async createCard(request: CreateCardRequest): Promise<BaseCard> {
    const tenantId = this.getTenantId();
    const response = await this.client.post<BaseCard>(CARD_ENDPOINTS.CREATE, request, {
      params: { tenant_id: tenantId },
    });
    return response.data;
  }

  /**
   * Update card
   */
  async updateCard(cardId: string, request: UpdateCardRequest): Promise<BaseCard> {
    const tenantId = this.getTenantId();
    const response = await this.client.put<BaseCard>(
      CARD_ENDPOINTS.UPDATE(cardId),
      request,
      { params: { tenant_id: tenantId } }
    );
    return response.data;
  }

  /**
   * Delete card
   */
  async deleteCard(cardId: string): Promise<void> {
    const tenantId = this.getTenantId();
    await this.client.delete(CARD_ENDPOINTS.DELETE(cardId), {
      params: { tenant_id: tenantId },
    });
  }

  /**
   * Get card relationships
   */
  async getRelationships(cardId: string): Promise<CardRelationship[]> {
    const tenantId = this.getTenantId();
    const response = await this.client.get<CardRelationship[]>(
      CARD_ENDPOINTS.RELATIONSHIPS,
      { params: { tenant_id: tenantId, card_id: cardId } }
    );
    return response.data;
  }

  /**
   * Create relationship between cards
   */
  async createRelationship(request: CreateRelationshipRequest): Promise<CardRelationship> {
    const tenantId = this.getTenantId();
    const response = await this.client.post<CardRelationship>(
      CARD_ENDPOINTS.CREATE_RELATIONSHIP,
      request,
      { params: { tenant_id: tenantId } }
    );
    return response.data;
  }

  /**
   * Delete relationship
   */
  async deleteRelationship(relationshipId: string): Promise<void> {
    const tenantId = this.getTenantId();
    await this.client.delete(CARD_ENDPOINTS.DELETE_RELATIONSHIP(relationshipId), {
      params: { tenant_id: tenantId },
    });
  }

  /**
   * Get all cards organized by type
   */
  async getContextAll(): Promise<Record<string, BaseCard[]>> {
    const tenantId = this.getTenantId();
    const response = await this.client.get<Record<string, BaseCard[]>>(
      CARD_ENDPOINTS.CONTEXT_ALL,
      { params: { tenant_id: tenantId } }
    );
    return response.data;
  }

  /**
   * Get RAG context text
   */
  async getRagContextText(): Promise<string> {
    const tenantId = this.getTenantId();
    const response = await this.client.get<{ context: string }>(
      CARD_ENDPOINTS.CONTEXT_RAG,
      { params: { tenant_id: tenantId } }
    );
    return response.data.context;
  }
}

export const cardApi = new CardApiClient();

