import React, {useState, useMemo} from 'react'
import styled from "styled-components";
import bg from './img/bg.png'
import ReactDOM from 'react-dom';
import {MainLayout} from './styles/Layouts'
import Orb from './Components/Orb/Orb'
import Navigation from './Components/Navigation/Navigation'
import Dashboard from './Components/Dashboard/Dashboard';
import Income from './Components/Income/Income'
import Expenses from './Components/Expenses/Expenses';
import ButtonNewTransaction from './Components/Navigation/ButtonNewTransaction';
import TransactionWindow from './Components/Navigation/TransactionWindow';
import { useGlobalContext } from './context/globalContext';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import TextField from '@mui/material/TextField';
import MenuItem from '@mui/material/MenuItem';

function App() {
  const [active, setActive] = useState(1)

  const global = useGlobalContext()
  console.log(global);

  const [isOpen, setIsOpen] = useState(false);
  const [amount, setAmount] = useState('');
  const [account, setAccount] = useState('');
  const [category, setCategory] = useState('');
  const [transactionType, setTransactionType] = useState('');

  const handleOpenDialog = () => {
    setIsOpen(true);
  };

  const handleCloseDialog = () => {
    setIsOpen(false);
  };

  const handleAmountChange = (event) => {
    setAmount(event.target.value);
  };

  const handleAccountChange = (event) => {
    setAccount(event.target.value);
  };

  const handleCategoryChange = (event) => {
    setCategory(event.target.value);
  };

  const handleTransactionTypeChange = (event) => {
    setTransactionType(event.target.value);
  };

  const handleSubmit = () => {
    // Отправка данных на сервер
    console.log('Отправленные данные:', amount, account, category, transactionType);
    // Закрытие окна
    handleCloseDialog();
  };

  const displayData = () => {
    switch(active){
      case 1:
        return <Dashboard />
      case 2:
        return <Dashboard />
      case 3:
        return <Income />
      case 4: 
        return <Expenses />
      default: 
        return <Dashboard />
    }
  }

  const orbMemo = useMemo(() => {
    return <Orb />
  },[])

  return (
    <AppStyled bg={bg} className="App">
      {orbMemo}
      <MainLayout>
        <Navigation active={active} setActive={setActive} />
        <main>
          {displayData()}

          <div>
      <Button variant="contained" onClick={handleOpenDialog}>
        Открыть окно
      </Button>
      <Dialog
        open={isOpen}
        onClose={handleCloseDialog}
        aria-labelledby="dialog-title"
        aria-describedby="dialog-description"
      >
        <DialogTitle id="dialog-title">Всплывающее окно</DialogTitle>
        <DialogContent>
          <DialogContentText id="dialog-description">
            <TextField
              autoFocus
              margin="dense"
              label="Сумма транзакции"
              type="number"
              fullWidth
              value={amount}
              onChange={handleAmountChange}
            />
            <TextField
              margin="dense"
              label="Счет"
              type="text"
              fullWidth
              value={account}
              onChange={handleAccountChange}
            />
            <TextField
              margin="dense"
              label="Категория"
              type="text"
              fullWidth
              value={category}
              onChange={handleCategoryChange}
            />
            <TextField
              select
              margin="dense"
              label="Тип транзакции"
              fullWidth
              value={transactionType}
              onChange={handleTransactionTypeChange}
            >
              <MenuItem value="income">Доход</MenuItem>
              <MenuItem value="expense">Расход</MenuItem>
            </TextField>
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Закрыть окно</Button>
          <Button onClick={handleSubmit}>Отправить</Button>
        </DialogActions>
      </Dialog>
    </div>
        </main>
      </MainLayout>
    </AppStyled>
  );
}

const AppStyled = styled.div`
  height: 100vh;
  background-image: url(${props => props.bg});
  position: relative;
  main{
    flex: 1;
    background: rgba(252, 246, 249, 0.78);
    border: 3px solid #FFFFFF;
    backdrop-filter: blur(4.5px);
    border-radius: 32px;
    overflow-x: hidden;
    &::-webkit-scrollbar{
      width: 0;
    }
  }
`;

export default App;
