import { useState, useCallback } from 'react';
import { useApi } from './useApi';
import { apiService } from '../services/api';
import { useSession } from '../context/SessionContext';
import toast from 'react-hot-toast';

/**
 * Custom hook for disaster response workflow
 */
export const useWorkflow = () => {
  const { execute, loading, error } = useApi();
  const { addSession } = useSession();
  const [workflowState, setWorkflowState] = useState(null);

  const executeWorkflow = useCallback(
    async (location, options = {}) => {
      const { onSuccess, onError } = options;

      try {
        const result = await execute(
          () => apiService.executeWorkflow(location),
          {
            showSuccessToast: true,
            successMessage: `Workflow executed successfully for ${location}`,
            onSuccess: (data) => {
              setWorkflowState(data);
              if (data.session_id) {
                addSession(data);
              }
              if (onSuccess) {
                onSuccess(data);
              }
            },
            onError,
          }
        );
        return result;
      } catch (err) {
        if (onError) {
          onError(err);
        }
        throw err;
      }
    },
    [execute, addSession]
  );

  const getWeather = useCallback(
    async (location, startDate, endDate) => {
      return execute(() => apiService.getWeather(location, startDate, endDate), {
        showSuccessToast: false,
      });
    },
    [execute]
  );

  const getSocialMedia = useCallback(
    async (location) => {
      return execute(() => apiService.getSocialMedia(location), {
        showSuccessToast: false,
      });
    },
    [execute]
  );

  const analyzeDisaster = useCallback(
    async (data) => {
      return execute(() => apiService.analyzeDisaster(data), {
        showSuccessToast: false,
      });
    },
    [execute]
  );

  const generatePlan = useCallback(
    async (data) => {
      return execute(() => apiService.generatePlan(data), {
        showSuccessToast: false,
      });
    },
    [execute]
  );

  const verifyPlan = useCallback(
    async (data) => {
      return execute(() => apiService.verifyPlan(data), {
        showSuccessToast: true,
        successMessage: 'Plan verified successfully',
      });
    },
    [execute]
  );

  const sendAlerts = useCallback(
    async (data) => {
      return execute(() => apiService.sendAlerts(data), {
        showSuccessToast: true,
        successMessage: 'Alerts sent successfully',
      });
    },
    [execute]
  );

  const resetWorkflow = useCallback(() => {
    setWorkflowState(null);
  }, []);

  return {
    workflowState,
    loading,
    error,
    executeWorkflow,
    getWeather,
    getSocialMedia,
    analyzeDisaster,
    generatePlan,
    verifyPlan,
    sendAlerts,
    resetWorkflow,
  };
};

export default useWorkflow;

