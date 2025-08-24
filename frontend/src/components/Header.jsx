import React from 'react';
import { useAuth } from '../hooks/useAuth';
import { useTheme } from '../hooks/useTheme';
import { FiSun, FiMoon, FiLogOut } from 'react-icons/fi';
import './Header.css';

const Header = () => {
  const { logout } = useAuth();
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="app-header">
      <h1 className="app-title">SpendWise AI</h1>
      <div className="header-actions">
        <button onClick={toggleTheme} className="icon-button">
          {theme === 'light' ? <FiMoon size={20} /> : <FiSun size={20} />}
        </button>
        <button onClick={logout} className="icon-button">
          <FiLogOut size={20} />
        </button>
      </div>
    </header>
  );
};

export default Header;