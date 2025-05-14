import React from 'react';
import { FiBell, FiUser, FiLogOut } from 'react-icons/fi';
import { useAuth } from '../context/AuthContext';

const Header = () => {
  const { currentUser, logout } = useAuth();

  if (!currentUser) return null;

  const handleLogout = async () => {
    await logout();
  };

  return (
    <header className="bg-white shadow-sm h-16 fixed top-0 right-0 left-64 z-10">
      <div className="flex items-center justify-between h-full px-6">
        <div>
          <h2 className="text-emerald text-lg font-semibold">
            {new Date().toLocaleDateString('id-ID', { 
              weekday: 'long', 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            })}
          </h2>
        </div>
        
        <div className="flex items-center space-x-4">
          <button className="relative p-2 rounded-full hover:bg-gray-100">
            <FiBell className="text-gray-600" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>
          
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-full bg-emerald text-eggshell flex items-center justify-center">
              <FiUser />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700">{currentUser.name}</p>
              <p className="text-xs text-gray-500">{currentUser.email}</p>
            </div>
            <button 
              onClick={handleLogout}
              className="p-2 rounded-full hover:bg-gray-100"
            >
              <FiLogOut className="text-gray-600" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;