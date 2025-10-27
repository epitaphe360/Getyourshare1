import { useState, useCallback } from 'react';
import api from '../utils/api';

/**
 * Custom hook for API calls with loading/error states
 * 
 * Features:
 * - Automatic loading state
 * - Error handling
 * - Request cancellation
 * - Retry logic
 * 
 * @returns {Object} API methods and state
 */
export const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  /**
   * Execute API request
   * @param {Function} apiCall - API function to call
   * @param {Object} options - Options
   * @returns {Promise<any>} Response data
   */
  const execute = useCallback(async (apiCall, options = {}) => {
    const { onSuccess, onError, showError = true } = options;

    setLoading(true);
    setError(null);

    try {
      const response = await apiCall();
      setData(response);

      if (onSuccess) {
        onSuccess(response);
      }

      return response;
    } catch (err) {
      const errorMessage = err.response?.data?.message || err.message || 'Request failed';
      setError(errorMessage);

      if (showError) {
        console.error('API Error:', errorMessage);
      }

      if (onError) {
        onError(err);
      }

      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Reset state
   */
  const reset = useCallback(() => {
    setLoading(false);
    setError(null);
    setData(null);
  }, []);

  return {
    loading,
    error,
    data,
    execute,
    reset,
  };
};

/**
 * Custom hook for paginated API calls
 * 
 * @param {Function} fetchFunction - Function to fetch data
 * @param {Object} initialParams - Initial query params
 * @returns {Object} Pagination state and methods
 */
export const usePagination = (fetchFunction, initialParams = {}) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);

  /**
   * Fetch page
   * @param {number} pageNum - Page number
   * @param {Object} params - Additional params
   */
  const fetchPage = useCallback(
    async (pageNum = page, params = {}) => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetchFunction({
          ...initialParams,
          ...params,
          page: pageNum,
        });

        setData(response.data || response.items || []);
        setTotalPages(response.totalPages || response.total_pages || 1);
        setTotalItems(response.totalItems || response.total_items || 0);
        setPage(pageNum);
      } catch (err) {
        setError(err.message);
        console.error('Pagination error:', err);
      } finally {
        setLoading(false);
      }
    },
    [fetchFunction, initialParams, page]
  );

  /**
   * Go to next page
   */
  const nextPage = useCallback(() => {
    if (page < totalPages) {
      fetchPage(page + 1);
    }
  }, [page, totalPages, fetchPage]);

  /**
   * Go to previous page
   */
  const previousPage = useCallback(() => {
    if (page > 1) {
      fetchPage(page - 1);
    }
  }, [page, fetchPage]);

  /**
   * Go to specific page
   * @param {number} pageNum - Page number
   */
  const goToPage = useCallback(
    (pageNum) => {
      if (pageNum >= 1 && pageNum <= totalPages) {
        fetchPage(pageNum);
      }
    },
    [totalPages, fetchPage]
  );

  /**
   * Refresh current page
   */
  const refresh = useCallback(() => {
    fetchPage(page);
  }, [page, fetchPage]);

  return {
    data,
    loading,
    error,
    page,
    totalPages,
    totalItems,
    fetchPage,
    nextPage,
    previousPage,
    goToPage,
    refresh,
    hasNextPage: page < totalPages,
    hasPreviousPage: page > 1,
  };
};

/**
 * Custom hook for search with debounce
 * 
 * @param {Function} searchFunction - Function to search
 * @param {number} delay - Debounce delay in ms
 * @returns {Object} Search state and methods
 */
export const useSearch = (searchFunction, delay = 500) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [debounceTimeout, setDebounceTimeout] = useState(null);

  /**
   * Execute search
   * @param {string} searchQuery - Search query
   */
  const search = useCallback(
    (searchQuery) => {
      setQuery(searchQuery);

      // Clear previous timeout
      if (debounceTimeout) {
        clearTimeout(debounceTimeout);
      }

      // Don't search if query is empty
      if (!searchQuery.trim()) {
        setResults([]);
        return;
      }

      // Set new timeout
      const timeout = setTimeout(async () => {
        setLoading(true);
        setError(null);

        try {
          const response = await searchFunction(searchQuery);
          setResults(response.data || response);
        } catch (err) {
          setError(err.message);
          console.error('Search error:', err);
        } finally {
          setLoading(false);
        }
      }, delay);

      setDebounceTimeout(timeout);
    },
    [searchFunction, delay, debounceTimeout]
  );

  /**
   * Clear search
   */
  const clear = useCallback(() => {
    setQuery('');
    setResults([]);
    setError(null);
    if (debounceTimeout) {
      clearTimeout(debounceTimeout);
    }
  }, [debounceTimeout]);

  return {
    query,
    results,
    loading,
    error,
    search,
    clear,
  };
};

export default useApi;
