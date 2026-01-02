/**
 * TanStack Query hook for spec generation.
 */

import { useMutation, UseMutationResult } from '@tanstack/react-query';
import { generateSpec, APIError } from '../api/client';
import type { StructuredSpec } from '../types/spec';

/**
 * Hook for generating specifications from user intent.
 *
 * @returns Mutation object with spec generation state
 */
export function useSpecGeneration(): UseMutationResult<StructuredSpec, APIError, string> {
  return useMutation<StructuredSpec, APIError, string>({
    mutationFn: (intent: string) => generateSpec(intent),
    onError: (error) => {
      console.error('Spec generation error:', error);
    },
    onSuccess: (spec) => {
      console.log('Spec generated successfully:', spec);
    },
  });
}
