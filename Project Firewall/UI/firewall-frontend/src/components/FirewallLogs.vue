<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { getLogs } from '../services/api';

const logs = ref([]);
const loading = ref(true);
const error = ref(null);

// Search and filter state
const searchQuery = ref('');
const selectedAction = ref('all');
const timeRange = ref('all');

// Function to fetch logs with optional filters
async function fetchLogs(filters = {}) {
  try {
    loading.value = true;
    // In a real implementation, you might pass filters to your API
    // For example: const response = await getLogs(filters);
    logs.value = await getLogs();
  } catch (err) {
    error.value = "Failed to fetch logs. Please try again later.";
    console.error("Failed to fetch logs:", err);
  } finally {
    loading.value = false;
  }
}

// Fetch logs on component mount
onMounted(() => {
  fetchLogs();
});

// Apply client-side filtering
const filteredLogs = computed(() => {
  return logs.value.filter(log => {
    // Filter by action type
    if (selectedAction.value !== 'all' && log.action !== selectedAction.value) {
      return false;
    }
    
    // Filter by time range
    if (timeRange.value !== 'all') {
      const now = new Date();
      const logDate = new Date(log.timestamp);
      const hoursDiff = (now - logDate) / (1000 * 60 * 60);
      
      if (timeRange.value === 'last24h' && hoursDiff > 24) {
        return false;
      } else if (timeRange.value === 'last7d' && hoursDiff > 168) {
        return false;
      }
    }
    
    // Search across all fields
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase();
      return log.source_ip.toLowerCase().includes(query) ||
             log.destination_ip.toLowerCase().includes(query) ||
             log.action.toLowerCase().includes(query) ||
             log.message.toLowerCase().includes(query) ||
             log.timestamp.toLowerCase().includes(query);
    }
    
    return true;
  });
});

// For debouncing search
let searchTimeout = null;
watch(searchQuery, () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout);
  }
  
  searchTimeout = setTimeout(() => {
    // If you want to trigger a server-side search instead
    // fetchLogs({ search: searchQuery.value });
  }, 300);
});

// Watch for filter changes
watch([selectedAction, timeRange], () => {
  // For server-side filtering, uncomment:
  // fetchLogs({ 
  //   action: selectedAction.value !== 'all' ? selectedAction.value : undefined,
  //   timeRange: timeRange.value !== 'all' ? timeRange.value : undefined
  // });
});

// Available actions for the dropdown
const actionOptions = [
  { value: 'all', label: 'All Actions' },
  { value: 'ALLOW', label: 'Allowed' },
  { value: 'BLOCK', label: 'Blocked' }
];

// Time range options
const timeRangeOptions = [
  { value: 'all', label: 'All Time' },
  { value: 'last24h', label: 'Last 24 Hours' },
  { value: 'last7d', label: 'Last 7 Days' }
];

// Function to refresh logs
function refreshLogs() {
  fetchLogs({
    action: selectedAction.value !== 'all' ? selectedAction.value : undefined,
    timeRange: timeRange.value !== 'all' ? timeRange.value : undefined,
    search: searchQuery.value || undefined
  });
}

// Function to clear all filters
function clearFilters() {
  searchQuery.value = '';
  selectedAction.value = 'all';
  timeRange.value = 'all';
}
</script>

<template>
  <div class="logs-container">
    <div class="card">
      <div class="card-header">
        <h1>Firewall Logs</h1>
        <div class="subtitle">Security Event Monitor</div>
      </div>
      
      <div class="filter-section">
        <div class="search-bar">
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Search logs..." 
            class="search-input"
          />
        </div>
        
        <div class="filters">
          <div class="filter-group">
            <label for="action-filter">Action:</label>
            <select id="action-filter" v-model="selectedAction" class="filter-select">
              <option v-for="option in actionOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>
          
          <div class="filter-group">
            <label for="time-filter">Time Range:</label>
            <select id="time-filter" v-model="timeRange" class="filter-select">
              <option v-for="option in timeRangeOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>
          
          <div class="filter-actions">
            <button @click="refreshLogs" class="btn btn-primary">Refresh</button>
            <button @click="clearFilters" class="btn btn-secondary">Clear Filters</button>
          </div>
        </div>
      </div>
      
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading logs...</p>
      </div>
      
      <div v-else-if="error" class="error-state">
        <div class="error-icon">!</div>
        <p>{{ error }}</p>
      </div>
      
      <div v-else class="table-container">
        <table>
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Source IP</th>
              <th>Destination IP</th>
              <th>Action</th>
              <th>Message</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in filteredLogs" :key="log.id" :class="{ 'blocked': log.action === 'BLOCK', 'allowed': log.action === 'ALLOW' }">
              <td>{{ log.timestamp }}</td>
              <td>{{ log.source_ip }}</td>
              <td>{{ log.destination_ip }}</td>
              <td>
                <span class="action-badge" :class="log.action.toLowerCase()">
                  {{ log.action }}
                </span>
              </td>
              <td>{{ log.message }}</td>
            </tr>
            <tr v-if="filteredLogs.length === 0">
              <td colspan="5" class="no-data">No matching logs found</td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="results-summary" v-if="!loading && !error">
        <span>Showing {{ filteredLogs.length }} of {{ logs.length }} logs</span>
        <span v-if="filteredLogs.length !== logs.length" class="filter-indicator">
          (Filters applied)
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.logs-container {
  max-width: 1200px;
  margin: 2rem auto;
  padding: 0 1rem;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  overflow: hidden;
}

.card-header {
  background: linear-gradient(135deg, #1a237e, #283593);
  color: white;
  padding: 1.5rem;
  position: relative;
}

h1 {
  margin: 0;
  font-size: 1.8rem;
  font-weight: 600;
}

.subtitle {
  margin-top: 0.5rem;
  opacity: 0.8;
  font-size: 1rem;
}

.filter-section {
  padding: 1rem;
  background-color: #f8f9fa;
  border-bottom: 1px solid #eaeaea;
}

.search-bar {
  margin-bottom: 1rem;
}

.search-input {
  width: 100%;
  padding: 0.7rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.95rem;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: flex-end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  min-width: 150px;
}

.filter-group label {
  margin-bottom: 0.3rem;
  font-size: 0.9rem;
  color: #666;
}

.filter-select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
}

.filter-actions {
  display: flex;
  gap: 0.5rem;
  margin-left: auto;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary {
  background-color: #3f51b5;
  color: white;
}

.btn-primary:hover {
  background-color: #303f9f;
}

.btn-secondary {
  background-color: #e0e0e0;
  color: #333;
}

.btn-secondary:hover {
  background-color: #d0d0d0;
}

.table-container {
  overflow-x: auto;
  padding: 1rem;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}

th, td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #eaeaea;
}

th {
  font-weight: 600;
  color: #424242;
  background-color: #f5f7fa;
  position: sticky;
  top: 0;
}

tbody tr {
  transition: background-color 0.2s;
}

tbody tr:hover {
  background-color: #f9fafc;
}

.action-badge {
  display: inline-block;
  padding: 0.3rem 0.6rem;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
}

.action-badge.block {
  background-color: #ffebee;
  color: #d32f2f;
}

.action-badge.allow {
  background-color: #e8f5e9;
  color: #2e7d32;
}

tr.blocked {
  background-color: rgba(255, 235, 238, 0.2);
}

tr.allowed {
  background-color: rgba(232, 245, 233, 0.2);
}

.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  color: #757575;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3f51b5;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.error-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: #ffebee;
  color: #d32f2f;
  font-size: 1.8rem;
  font-weight: bold;
  margin-bottom: 1rem;
}

.no-data {
  text-align: center;
  color: #9e9e9e;
  padding: 3rem 0;
}

.results-summary {
  padding: 1rem;
  text-align: right;
  color: #757575;
  font-size: 0.9rem;
  border-top: 1px solid #eaeaea;
}

.filter-indicator {
  font-style: italic;
  margin-left: 0.5rem;
  color: #9e9e9e;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .card-header {
    padding: 1.2rem;
  }
  
  h1 {
    font-size: 1.5rem;
  }
  
  .filters {
    flex-direction: column;
  }
  
  .filter-group {
    width: 100%;
  }
  
  .filter-actions {
    margin-left: 0;
    margin-top: 1rem;
    width: 100%;
    justify-content: space-between;
  }
  
  .btn {
    flex: 1;
  }
  
  th, td {
    padding: 0.8rem;
    font-size: 0.9rem;
  }
}
</style>