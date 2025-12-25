/**
 * Refine data provider for API communication.
 * 
 * Implements the DataProvider interface for CRUD operations.
 */
import { DataProvider } from '@refinedev/core';
import { apiClient, getErrorMessage } from '../utils/api';
import { AxiosResponse } from 'axios';

export const dataProvider: DataProvider = {
  // Get list of resources
  getList: async ({ resource, pagination, filters, sorters, meta }) => {
    const url = `/${resource}`;
    
    const params: any = {};
    
    if (pagination) {
      params.offset = ((pagination.current || 1) - 1) * (pagination.pageSize || 10);
      params.limit = pagination.pageSize || 10;
    }
    
    if (sorters && sorters.length > 0) {
      params.sort_by = sorters[0].field;
      params.sort_order = sorters[0].order;
    }
    
    if (filters) {
      filters.forEach((filter) => {
        if ('field' in filter) {
          params[filter.field] = filter.value;
        }
      });
    }
    
    try {
      const response: AxiosResponse = await apiClient.get(url, { params });
      
      return {
        data: response.data.data || response.data,
        total: response.data.total || response.data.length,
      };
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  // Get one resource by ID
  getOne: async ({ resource, id, meta }) => {
    const url = `/${resource}/${id}`;
    
    try {
      const response: AxiosResponse = await apiClient.get(url);
      
      return {
        data: response.data,
      };
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  // Create new resource
  create: async ({ resource, variables, meta }) => {
    const url = `/${resource}`;
    
    try {
      const response: AxiosResponse = await apiClient.post(url, variables);
      
      return {
        data: response.data,
      };
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  // Update resource
  update: async ({ resource, id, variables, meta }) => {
    const url = `/${resource}/${id}`;
    
    try {
      const response: AxiosResponse = await apiClient.put(url, variables);
      
      return {
        data: response.data,
      };
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  // Delete resource
  deleteOne: async ({ resource, id, meta }) => {
    const url = `/${resource}/${id}`;
    
    try {
      const response: AxiosResponse = await apiClient.delete(url);
      
      return {
        data: response.data,
      };
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },

  // Get API URL
  getApiUrl: () => {
    return apiClient.defaults.baseURL || '/api';
  },

  // Custom method support (for actions like testing connections, executing queries)
  custom: async ({ url, method, filters, sorters, payload, query, headers }) => {
    let requestUrl = url;
    
    if (query) {
      const params = new URLSearchParams(query);
      requestUrl = `${url}?${params.toString()}`;
    }
    
    try {
      const response: AxiosResponse = await apiClient({
        url: requestUrl,
        method: method || 'get',
        data: payload,
        headers,
      });
      
      return {
        data: response.data,
      };
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  },
};
