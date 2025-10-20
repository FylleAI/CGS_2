/**
 * Renderer Registry
 * 
 * Metadata-driven rendering system for CGS results.
 * Backend specifies display_type, frontend uses registry to find appropriate renderer.
 */

import type { OnboardingSession } from '@/types/onboarding';

export interface RendererConfig {
  component: React.ComponentType<any>;
  dataExtractor: (session: OnboardingSession) => any;
}

class RendererRegistry {
  private renderers: Map<string, RendererConfig> = new Map();

  /**
   * Register a renderer for a specific display type.
   * 
   * @param displayType - Display type from backend (e.g., "analytics_dashboard", "content_preview")
   * @param component - React component to render
   * @param dataExtractor - Function to extract data from session
   */
  register(
    displayType: string,
    component: React.ComponentType<any>,
    dataExtractor: (session: OnboardingSession) => any
  ): void {
    this.renderers.set(displayType, { component, dataExtractor });
    console.log(`✅ Renderer registered: ${displayType}`);
  }

  /**
   * Get renderer configuration for a display type.
   * 
   * @param displayType - Display type from backend
   * @returns Renderer config or undefined if not found
   */
  getRenderer(displayType: string): RendererConfig | undefined {
    return this.renderers.get(displayType);
  }

  /**
   * Check if a renderer is registered for a display type.
   * 
   * @param displayType - Display type to check
   * @returns True if renderer exists
   */
  hasRenderer(displayType: string): boolean {
    return this.renderers.has(displayType);
  }

  /**
   * Get all registered display types.
   * 
   * @returns Array of display types
   */
  getRegisteredTypes(): string[] {
    return Array.from(this.renderers.keys());
  }
}

// Global singleton instance
export const rendererRegistry = new RendererRegistry();

