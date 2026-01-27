/**
 * Navbar Component
 * 
 * Top navigation bar for admin panel with logout
 */

import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import Button from '../common/Button';

export default function Navbar() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/admin/login');
  };

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        
        {/* Logo */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-indigo-600 rounded-full flex items-center justify-center">
            <span className="text-white text-xl font-bold">SB</span>
          </div>
          <div>
            <h1 className="font-semibold text-gray-900">SmartByte Admin</h1>
            <p className="text-xs text-gray-500">פאנל ניהול</p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-4">
          {/* Stats Badge */}
          <div className="hidden md:flex items-center gap-2 px-3 py-2 bg-green-50 rounded-lg">
            <span className="w-2 h-2 bg-green-500 rounded-full"></span>
            <span className="text-sm text-green-700 font-medium">מערכת פעילה</span>
          </div>

          {/* Logout Button */}
          <Button
            variant="secondary"
            size="sm"
            onClick={handleLogout}
          >
            התנתק
          </Button>
        </div>
      </div>
    </nav>
  );
}