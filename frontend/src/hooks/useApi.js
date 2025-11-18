import { useState, useCallback } from 'react';
import { useLoading } from '../context/LoadingContext';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';

/**
 * Custom hook for API calls with loading and error handling
 */
export const useApi = () => {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const { startLoading, stopLoading } = useLoading();

  const execute = useCallback(
    async (apiCall, options = {}) => {
      const {
        showLoading = true,
        showSuccessToast = false,
        showErrorToast = true,
        successMessage = 'Operation successful',
        onSuccess,
        onError,
      } = options;

      setLoading(true);
      setError(null);
      if (showLoading) {
        startLoading();
      }

      try {
        const response = await apiCall();
        setData(response.data);
        if (showSuccessToast) {
          toast.success(successMessage);
        }
        if (onSuccess) {
          onSuccess(response.data);
        }
        return response.data;
      } catch (err) {
        const errorMessage =
          err.response?.data?.detail ||
          err.response?.data?.message ||
          err.message ||
          'An error occurred';
        setError(errorMessage);
        if (showErrorToast && !err.response?.config?.skipErrorToast) {
          toast.error(errorMessage);
        }
        if (onError) {
          onError(err);
        }
        throw err;
      } finally {
        setLoading(false);
        if (showLoading) {
          stopLoading();
        }
      }
    },
    [startLoading, stopLoading]
  );

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
  }, []);

  return {
    data,
    error,
    loading,
    execute,
    reset,
  };
};

export default useApi;

