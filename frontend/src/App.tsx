import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';

// 页面组件
import Layout from './components/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import RealtimeTraining from './pages/RealtimeTraining';
import VideoAnalysis from './pages/VideoAnalysis';
import TrainingRecords from './pages/TrainingRecords';
import DataAnalysis from './pages/DataAnalysis';
import Courses from './pages/Courses';
import Achievements from './pages/Achievements';
import Profile from './pages/Profile';

import './App.css';

const App: React.FC = () => {
  return (
    <ConfigProvider locale={zhCN}>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="realtime" element={<RealtimeTraining />} />
            <Route path="video-analysis" element={<VideoAnalysis />} />
            <Route path="records" element={<TrainingRecords />} />
            <Route path="analysis" element={<DataAnalysis />} />
            <Route path="courses" element={<Courses />} />
            <Route path="achievements" element={<Achievements />} />
            <Route path="profile" element={<Profile />} />
          </Route>
        </Routes>
      </Router>
    </ConfigProvider>
  );
};

export default App;
