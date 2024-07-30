import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const [login, setLogin] = useState('');
  const navigate = useNavigate();

  const handleLogin = async () => {
    try {
      const response = await axios.post('/get_user', { login });
      if (response.status === 200) {
        localStorage.setItem('user', JSON.stringify(response.data));
        navigate('/books');
      }
    } catch (error) {
      console.error("Login error:", error);
    }
  };

  return (
    <div>
      <h2>Login</h2>
      <input
        type="text"
        value={login}
        onChange={(e) => setLogin(e.target.value)}
        placeholder="Enter your login"
      />
      <button onClick={handleLogin}>Login</button>
    </div>
  );
};

export default Login;
