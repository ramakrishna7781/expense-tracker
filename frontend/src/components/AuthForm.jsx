import React, { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { loginUser, registerUser } from '../api';
import './AuthForm.css';
import Loader from './Loader';

const AuthForm = ({ isLogin }) => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      let response;
      if (isLogin) {
        response = await loginUser({ email, password });
      } else {
        response = await registerUser({ name, email, password });
      }
      login(response.data.access_token);
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="auth-form">
      {!isLogin && (
        <div className="form-group">
          <input
            type="text"
            placeholder="Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>
      )}
      <div className="form-group">
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </div>
      <div className="form-group">
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>
      {error && <p className="error-message">{error}</p>}
      <button type="submit" className="submit-button" disabled={loading}>
        {loading ? <Loader /> : (isLogin ? 'Login' : 'Register')}
      </button>
    </form>
  );
};

export default AuthForm;