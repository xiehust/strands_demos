import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/common/Layout';
import { ChatPage } from './pages/ChatPage';
import { AgentsPage } from './pages/AgentsPage';
import { CreateAgentPage } from './pages/CreateAgentPage';
import { SkillsPage } from './pages/SkillsPage';
import { UploadSkillPage } from './pages/UploadSkillPage';
import { CreateSkillPage } from './pages/CreateSkillPage';
import { MCPPage } from './pages/MCPPage';
import { AddMCPServerPage } from './pages/AddMCPServerPage';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<ChatPage />} />
          <Route path="/agents" element={<AgentsPage />} />
          <Route path="/agents/create" element={<CreateAgentPage />} />
          <Route path="/skills" element={<SkillsPage />} />
          <Route path="/skills/upload" element={<UploadSkillPage />} />
          <Route path="/skills/create" element={<CreateSkillPage />} />
          <Route path="/mcp" element={<MCPPage />} />
          <Route path="/mcp/add" element={<AddMCPServerPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
