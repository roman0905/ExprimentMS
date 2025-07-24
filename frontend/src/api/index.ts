import axios from 'axios';

// 创建 axios 实例
const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 用户相关接口
export const userApi = {
  // 登录
  login: (data: { username: string; password: string }) => 
    api.post('/api/auth/login', data),
  
  // 注册
  register: (data: { username: string; password: string }) => 
    api.post('/api/auth/register', data),
  
  // 获取当前用户信息
  getCurrentUser: () => 
    api.get('/api/auth/me'),
  
  // 登出
  logout: () => 
    api.post('/api/auth/logout'),
  
  // 获取用户列表
  getUsers: () => 
    api.get('/api/auth/users'),
  
  // 创建用户
  createUser: (data: any) => 
    api.post('/api/auth/users', data),
  
  // 更新用户
  updateUser: (userId: number, data: any) => 
    api.put(`/api/auth/users/${userId}`, data),
  
  // 删除用户
  deleteUser: (userId: number) => 
    api.delete(`/api/auth/users/${userId}`),
  
  // 获取用户权限
  getUserPermissions: (userId: number) => 
    api.get(`/api/auth/users/${userId}/permissions`),
  
  // 分配权限
  assignPermissions: (data: any) => 
    api.post('/api/auth/assign-permissions', data),
};

// 导出 api 实例和用户接口
export { api };
export default api;