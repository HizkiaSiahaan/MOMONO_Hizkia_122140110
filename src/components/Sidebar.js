import React from 'react';
import { NavLink } from 'react-router-dom';
import { FiHome, FiDollarSign, FiCreditCard, FiPieChart, FiBell, FiSettings } from 'react-icons/fi';
import { useAuth } from '../context/AuthContext';

const Sidebar = () => {
  const { currentUser } = useAuth();

  if (!currentUser) return null;

  return (
    <div className="h-screen w-64 bg-emerald text-eggshell fixed left-0 top-0 overflow-y-auto">
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-8">MOMONO</h1>
        <p className="text-sm opacity-70 mb-8">Modern Money Notes</p>
        
        <nav>
          <ul className="space-y-2">
            <li>
              <NavLink 
                to="/dashboard" 
                className={({ isActive }) => 
                  `flex items-center p-3 rounded-lg transition-all ${
                    isActive 
                      ? 'bg-eggshell text-emerald font-medium' 
                      : 'hover:bg-emerald/80'
                  }`
                }
              >
                <FiHome className="mr-3" />
                Dashboard
              </NavLink>
            </li>
            <li>
              <NavLink 
                to="/budget" 
                className={({ isActive }) => 
                  `flex items-center p-3 rounded-lg transition-all ${
                    isActive 
                      ? 'bg-eggshell text-emerald font-medium' 
                      : 'hover:bg-emerald/80'
                  }`
                }
              >
                <FiDollarSign className="mr-3" />
                Anggaran
              </NavLink>
            </li>
            <li>
              <NavLink 
                to="/transactions" 
                className={({ isActive }) => 
                  `flex items-center p-3 rounded-lg transition-all ${
                    isActive 
                      ? 'bg-eggshell text-emerald font-medium' 
                      : 'hover:bg-emerald/80'
                  }`
                }
              >
                <FiCreditCard className="mr-3" />
                Transaksi
              </NavLink>
            </li>
            <li>
              <NavLink 
                to="/stats" 
                className={({ isActive }) => 
                  `flex items-center p-3 rounded-lg transition-all ${
                    isActive 
                      ? 'bg-eggshell text-emerald font-medium' 
                      : 'hover:bg-emerald/80'
                  }`
                }
              >
                <FiPieChart className="mr-3" />
                Statistik
              </NavLink>
            </li>
            <li>
              <NavLink 
                to="/notifications" 
                className={({ isActive }) => 
                  `flex items-center p-3 rounded-lg transition-all ${
                    isActive 
                      ? 'bg-eggshell text-emerald font-medium' 
                      : 'hover:bg-emerald/80'
                  }`
                }
              >
                <FiBell className="mr-3" />
                Notifikasi
              </NavLink>
            </li>
          </ul>
        </nav>
      </div>
      
      <div className="absolute bottom-0 left-0 w-full p-6">
        <NavLink 
          to="/settings" 
          className={({ isActive }) => 
            `flex items-center p-3 rounded-lg transition-all ${
              isActive 
                ? 'bg-eggshell text-emerald font-medium' 
                : 'hover:bg-emerald/80'
            }`
          }
        >
          <FiSettings className="mr-3" />
          Pengaturan
        </NavLink>
      </div>
    </div>
  );
};

export default Sidebar;