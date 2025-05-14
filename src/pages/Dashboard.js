import React, { useState, useEffect } from 'react';
import {
  FiArrowUp,
  FiArrowDown,
  FiAlertTriangle,
  FiDollarSign,
  FiCreditCard
} from 'react-icons/fi';
import { transactionAPI, budgetAPI } from '../api/api';
import { Link } from 'react-router-dom';

// Dummy data
const dummyData = {
  totalBudget: 5000000,
  totalExpense: 3200000,
  totalIncome: 6500000,
  recentTransactions: [
    { id: 1, type: 'expense', amount: 150000, category: 'Makanan', date: '2023-04-01', description: 'Makan siang' },
    { id: 2, type: 'income', amount: 5000000, category: 'Gaji', date: '2023-04-01', description: 'Gaji bulanan' },
    { id: 3, type: 'expense', amount: 500000, category: 'Transportasi', date: '2023-03-30', description: 'Bensin' },
    { id: 4, type: 'expense', amount: 1000000, category: 'Hiburan', date: '2023-03-29', description: 'Nonton konser' },
  ],
  budgetWarnings: [
    { id: 1, category: 'Hiburan', budgeted: 1000000, spent: 950000 },
    { id: 2, category: 'Makanan', budgeted: 1500000, spent: 1200000 },
  ]
};

const Dashboard = () => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // const budgetResponse = await budgetAPI.getAll();
        // const transactionResponse = await transactionAPI.getAll({ limit: 5 });
        setSummary(dummyData);
      } catch (err) {
        setError('Gagal memuat data dashboard');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 text-red-700 p-4 rounded-md">
        {error}
      </div>
    );
  }

  const { totalBudget, totalExpense, totalIncome, recentTransactions, budgetWarnings } = summary;
  const remainingBudget = totalBudget - totalExpense;
  const percentageUsed = (totalExpense / totalBudget) * 100;

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Dashboard</h1>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-600 font-medium">Sisa Anggaran Bulan Ini</h3>
            <FiDollarSign className="text-emerald-500" />
          </div>
          <p className="text-3xl font-bold text-gray-800">
            Rp {remainingBudget.toLocaleString('id-ID')}
          </p>
          <div className="mt-4">
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div
                className={`h-2.5 rounded-full ${percentageUsed > 80 ? 'bg-red-500' : 'bg-emerald-500'}`}
                style={{ width: `${percentageUsed}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-500 mt-2">
              {percentageUsed.toFixed(0)}% dari Rp {totalBudget.toLocaleString('id-ID')} terpakai
            </p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-600 font-medium">Total Pemasukan</h3>
            <FiArrowUp className="text-green-500" />
          </div>
          <p className="text-3xl font-bold text-gray-800">
            Rp {totalIncome.toLocaleString('id-ID')}
          </p>
          <p className="text-sm text-gray-500 mt-4">Bulan April 2023</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-600 font-medium">Total Pengeluaran</h3>
            <FiArrowDown className="text-red-500" />
          </div>
          <p className="text-3xl font-bold text-gray-800">
            Rp {totalExpense.toLocaleString('id-ID')}
          </p>
          <p className="text-sm text-gray-500 mt-4">Bulan April 2023</p>
        </div>
      </div>

      {/* Budget Warnings */}
      {budgetWarnings && budgetWarnings.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-8">
          <h3 className="flex items-center text-yellow-800 font-medium mb-2">
            <FiAlertTriangle className="mr-2" />
            Peringatan Anggaran
          </h3>
          <div className="space-y-2">
            {budgetWarnings.map(warning => (
              <div key={warning.id} className="flex justify-between items-center">
                <p className="text-yellow-700">
                  Kategori <span className="font-medium">{warning.category}</span> telah mencapai {((warning.spent / warning.budgeted) * 100).toFixed(0)}% dari anggaran
                </p>
                <Link to="/budget" className="text-sm text-emerald-600 hover:underline">
                  Lihat Detail
                </Link>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Transactions */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-medium text-gray-800">Transaksi Terbaru</h3>
            <Link to="/transactions" className="text-emerald-600 hover:underline">
              Lihat Semua
            </Link>
          </div>
        </div>

        <div className="divide-y divide-gray-200">
          {recentTransactions.map(transaction => (
            <div key={transaction.id} className="p-4 flex items-center justify-between">
              <div className="flex items-center">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                  transaction.type === 'income' ? 'bg-green-100' : 'bg-red-100'
                }`}>
                  {transaction.type === 'income' ? (
                    <FiArrowUp className="text-green-500" />
                  ) : (
                    <FiArrowDown className="text-red-500" />
                  )}
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-800">{transaction.description}</p>
                  <p className="text-xs text-gray-500">{transaction.category} • {new Date(transaction.date).toLocaleDateString('id-ID')}</p>
                </div>
              </div>
              <p className={`font-medium ${
                transaction.type === 'income' ? 'text-green-600' : 'text-red-600'
              }`}>
                {transaction.type === 'income' ? '+' : '-'} Rp {transaction.amount.toLocaleString('id-ID')}
              </p>
            </div>
          ))}
        </div>

        <div className="p-4 text-center">
          <Link
            to="/transactions/create"
            className="inline-flex items-center text-emerald-600 hover:underline"
          >
            <FiCreditCard className="mr-2" />
            Tambah Transaksi Baru
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
