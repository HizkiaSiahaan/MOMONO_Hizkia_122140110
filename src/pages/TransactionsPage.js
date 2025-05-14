import React, { useState, useEffect } from 'react';
import {
  FiPlus, FiFilter, FiEdit2, FiTrash2, FiDownload,
  FiArrowUp, FiArrowDown, FiAlertCircle
} from 'react-icons/fi';
import { transactionAPI, categoryAPI } from '../api/api';

const dummyTransactions = [
  { id: 1, type: 'expense', amount: 150000, category: 'Makanan', date: '2023-04-01', description: 'Makan siang' },
  { id: 2, type: 'income', amount: 5000000, category: 'Gaji', date: '2023-04-01', description: 'Gaji bulanan' },
  { id: 3, type: 'expense', amount: 500000, category: 'Transportasi', date: '2023-03-30', description: 'Bensin' },
  { id: 4, type: 'expense', amount: 1000000, category: 'Hiburan', date: '2023-03-29', description: 'Nonton konser' },
  { id: 5, type: 'expense', amount: 350000, category: 'Belanja', date: '2023-03-28', description: 'Belanja bulanan' },
  { id: 6, type: 'income', amount: 1000000, category: 'Freelance', date: '2023-03-27', description: 'Proyek desain' },
];

const dummyCategories = [
  { id: 1, name: 'Makanan', type: 'expense' },
  { id: 2, name: 'Transportasi', type: 'expense' },
  { id: 3, name: 'Hiburan', type: 'expense' },
  { id: 4, name: 'Belanja', type: 'expense' },
  { id: 5, name: 'Gaji', type: 'income' },
  { id: 6, name: 'Freelance', type: 'income' },
  { id: 7, name: 'Lainnya', type: 'both' },
];

const TransactionsPage = () => {
  const [transactions, setTransactions] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [showForm, setShowForm] = useState(false);
  const [formMode, setFormMode] = useState('create');
  const [selectedTransaction, setSelectedTransaction] = useState(null);
  const [formData, setFormData] = useState({
    type: 'expense',
    amount: '',
    category: '',
    date: new Date().toISOString().split('T')[0],
    description: '',
  });

  const [showFilter, setShowFilter] = useState(false);
  const [filters, setFilters] = useState({
    type: 'all',
    category: 'all',
    startDate: '',
    endDate: '',
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        setTransactions(dummyTransactions);
        setCategories(dummyCategories);
      } catch (err) {
        setError('Gagal memuat data transaksi');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const handleCreateTransaction = () => {
    setFormMode('create');
    setSelectedTransaction(null);
    setFormData({
      type: 'expense',
      amount: '',
      category: '',
      date: new Date().toISOString().split('T')[0],
      description: '',
    });
    setShowForm(true);
  };

  const handleEditTransaction = (transaction) => {
    setFormMode('edit');
    setSelectedTransaction(transaction);
    setFormData({
      type: transaction.type,
      amount: transaction.amount,
      category: transaction.category,
      date: transaction.date,
      description: transaction.description,
    });
    setShowForm(true);
  };

  const handleDeleteTransaction = async (id) => {
    if (window.confirm('Apakah Anda yakin ingin menghapus transaksi ini?')) {
      try {
        setTransactions(transactions.filter(t => t.id !== id));
      } catch (err) {
        setError('Gagal menghapus transaksi');
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (formMode === 'create') {
        const newTransaction = {
          id: Date.now(),
          ...formData,
          amount: parseFloat(formData.amount),
        };
        setTransactions([newTransaction, ...transactions]);
      } else {
        const updated = transactions.map(t => t.id === selectedTransaction.id ? { ...formData, id: t.id, amount: parseFloat(formData.amount) } : t);
        setTransactions(updated);
      }
      setShowForm(false);
    } catch (err) {
      setError(`Gagal ${formMode === 'create' ? 'membuat' : 'mengupdate'} transaksi`);
    }
  };

  const applyFilters = () => {
    return transactions.filter(t => {
      if (filters.type !== 'all' && t.type !== filters.type) return false;
      if (filters.category !== 'all' && t.category !== filters.category) return false;
      if (filters.startDate && new Date(t.date) < new Date(filters.startDate)) return false;
      if (filters.endDate && new Date(t.date) > new Date(filters.endDate)) return false;
      return true;
    });
  };

  const filteredTransactions = applyFilters();

  if (loading) {
    return <div className="flex justify-center items-center h-full">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500"></div>
    </div>;
  }

  return (
    <div className="p-6">
      {/* Konten halaman transaksi */}
      {/* Untuk mempersingkat, konten detail akan di-render dari state di atas */}
    </div>
  );
};

export default TransactionsPage;