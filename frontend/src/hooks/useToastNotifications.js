import { useCallback } from 'react';
import toast from 'react-hot-toast';

/**
 * Custom hook for toast notifications
 */
export const useToastNotifications = () => {
  const showSuccess = useCallback((message) => {
    toast.success(message, {
      duration: 4000,
      position: 'top-right',
    });
  }, []);

  const showError = useCallback((message) => {
    toast.error(message, {
      duration: 5000,
      position: 'top-right',
    });
  }, []);

  const showInfo = useCallback((message) => {
    toast(message, {
      duration: 4000,
      position: 'top-right',
      icon: 'ℹ️',
    });
  }, []);

  const showWarning = useCallback((message) => {
    toast(message, {
      duration: 4000,
      position: 'top-right',
      icon: '⚠️',
    });
  }, []);

  const showLoading = useCallback((message) => {
    return toast.loading(message, {
      position: 'top-right',
    });
  }, []);

  const dismiss = useCallback((toastId) => {
    toast.dismiss(toastId);
  }, []);

  return {
    showSuccess,
    showError,
    showInfo,
    showWarning,
    showLoading,
    dismiss,
  };
};

export default useToastNotifications;

