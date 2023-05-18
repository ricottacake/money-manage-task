import {dashboard, expenses, transactions, trend} from '../utils/Icons'

export const menuItems = [
    {
        id: 1,
        title: 'Dashboard',
        icon: dashboard,
        link: '/dashboard'
    },
    {
        id: 2,
        title: "Incomes & Expenses",
        icon: trend,
        link: "/dashboard",
    },
    {
        id: 3,
        title: "Credit",
        icon: expenses,
        link: "/dashboard",
    },

    {
        id: 4,
        title: "Debits",
        icon: expenses,
        link: "/dashboard",
    }
]