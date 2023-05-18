import React, { useState } from 'react';

const TransactionWindow = ({ onClose }) => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');

  const handleNameChange = (e) => {
    setName(e.target.value);
  };

  const handleEmailChange = (e) => {
    setEmail(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();


    const data = {
      name: name,
      email: email,
    };

    setName('');
    setEmail('');
    onClose(); 
  };

  return (
    <div className="transaction-window">
      <form onSubmit={handleSubmit}>
        <label>
          Имя:
          <input type="text" value={name} onChange={handleNameChange} />
        </label>
        <br />
        <label>
          Email:
          <input type="email" value={email} onChange={handleEmailChange} />
        </label>
        <br />
        <button type="submit">send</button>
        <button onClick={onClose}>close</button>
      </form>
    </div>
  );
};

export default TransactionWindow;
