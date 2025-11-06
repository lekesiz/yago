/**
 * usePagination Hook
 * Custom hook for managing pagination state and API calls
 */
import { useState, useEffect, useCallback } from 'react';
import { logger } from '../services/logger';

interface PaginationMeta {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

interface PaginationState<T> {
  data: T[];
  pagination: PaginationMeta | null;
  loading: boolean;
  error: string | null;
}

interface UsePaginationOptions {
  initialPage?: number;
  initialPageSize?: number;
  initialSortBy?: string;
  initialOrder?: 'asc' | 'desc';
}

interface UsePaginationReturn<T> {
  // State
  data: T[];
  pagination: PaginationMeta | null;
  loading: boolean;
  error: string | null;

  // Pagination controls
  page: number;
  pageSize: number;
  sortBy: string;
  order: 'asc' | 'desc';

  // Actions
  setPage: (page: number) => void;
  setPageSize: (pageSize: number) => void;
  setSortBy: (sortBy: string) => void;
  setOrder: (order: 'asc' | 'desc') => void;
  refetch: () => Promise<void>;
  reset: () => void;
}

export function usePagination<T = any>(
  fetchFunction: (params: {
    page: number;
    page_size: number;
    sort_by: string;
    order: 'asc' | 'desc';
  }) => Promise<{ data: T[]; pagination: PaginationMeta }>,
  options: UsePaginationOptions = {}
): UsePaginationReturn<T> {
  const {
    initialPage = 1,
    initialPageSize = 20,
    initialSortBy = 'created_at',
    initialOrder = 'desc',
  } = options;

  // Pagination parameters
  const [page, setPage] = useState(initialPage);
  const [pageSize, setPageSize] = useState(initialPageSize);
  const [sortBy, setSortBy] = useState(initialSortBy);
  const [order, setOrder] = useState<'asc' | 'desc'>(initialOrder);

  // Data state
  const [state, setState] = useState<PaginationState<T>>({
    data: [],
    pagination: null,
    loading: false,
    error: null,
  });

  // Fetch data
  const fetchData = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      logger.info('Fetching paginated data', {
        page,
        pageSize,
        sortBy,
        order,
      });

      const result = await fetchFunction({
        page,
        page_size: pageSize,
        sort_by: sortBy,
        order,
      });

      setState({
        data: result.data,
        pagination: result.pagination,
        loading: false,
        error: null,
      });

      logger.info('Paginated data fetched successfully', {
        total: result.pagination.total,
        page: result.pagination.page,
      });
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to fetch data';

      logger.error('Failed to fetch paginated data', error as Error, {
        page,
        pageSize,
        sortBy,
        order,
      });

      setState((prev) => ({
        ...prev,
        loading: false,
        error: errorMessage,
      }));
    }
  }, [fetchFunction, page, pageSize, sortBy, order]);

  // Fetch data when parameters change
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Handle page change
  const handlePageChange = useCallback((newPage: number) => {
    setPage(newPage);
  }, []);

  // Handle page size change
  const handlePageSizeChange = useCallback((newPageSize: number) => {
    setPageSize(newPageSize);
    setPage(1); // Reset to first page when page size changes
  }, []);

  // Handle sort by change
  const handleSortByChange = useCallback((newSortBy: string) => {
    setSortBy(newSortBy);
    setPage(1); // Reset to first page when sorting changes
  }, []);

  // Handle order change
  const handleOrderChange = useCallback((newOrder: 'asc' | 'desc') => {
    setOrder(newOrder);
    setPage(1); // Reset to first page when order changes
  }, []);

  // Reset pagination to initial state
  const reset = useCallback(() => {
    setPage(initialPage);
    setPageSize(initialPageSize);
    setSortBy(initialSortBy);
    setOrder(initialOrder);
  }, [initialPage, initialPageSize, initialSortBy, initialOrder]);

  return {
    // State
    data: state.data,
    pagination: state.pagination,
    loading: state.loading,
    error: state.error,

    // Pagination controls
    page,
    pageSize,
    sortBy,
    order,

    // Actions
    setPage: handlePageChange,
    setPageSize: handlePageSizeChange,
    setSortBy: handleSortByChange,
    setOrder: handleOrderChange,
    refetch: fetchData,
    reset,
  };
}

export default usePagination;
