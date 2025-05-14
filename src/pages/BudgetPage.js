import React, { useState, useEffect } from 'react';
import { FiPlus, FiEdit2, FiTrash2, FiAlertCircle } from 'react-icons/fi';
import { budgetAPI, categoryAPI } from '../api/api';
import { useAuth } from '../context/AuthContext';

// Dummy data
const dummyBudgets = [
  { id: 1, category: 'Makanan', amount: 1500000, spent: 1200000 },
  { id: 2, category: 'Transportasi', amount: 800000, spent: 600000 },
  { id: 3, category: 'Hiburan', amount: 1000000, spent: 950000 },
  { id: 4, category: 'Belanja', amount: 1200000, spent: 800000 },
  { id: 5, category: 'Lainnya', amount: 500000, spent: 250000 },
];

const dummyCategories = [
  { id: 1, name: 'Makanan' },
  { id: 2, name: 'Transportasi' },
  { id: 3, name: 'Hiburan' },
  { id: 4, name: 'Belanja' },
  { id: 5, name: 'Lainnya' },
];

const BudgetPage = () => {
  const [budgets, setBudgets] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [showForm, setShowForm] = useState(false);
  const [formMode, setFormMode] = useState('create');
  const [selectedBudget, setSelectedBudget] = useState(null);
  const [formData, setFormData] = useState({
    category: '',
    amount: '',
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        // const budgetResponse = await budgetAPI.getAll();
        // const categoryResponse = await categoryAPI.getAll();

        setBudgets(dummyBudgets);
        setCategories(dummyCategories);
      } catch (err) {
        setError('Gagal memuat data anggaran');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleCreateBudget = () => {
    setFormMode('create');
    setSelectedBudget(null);
    setFormData({ category: '', amount: '' });
    setShowForm(true);
  };

  const handleEditBudget = (budget) => {
    setFormMode('edit');
    setSelectedBudget(budget);
    setFormData({ category: budget.category, amount: budget.amount });
    setShowForm(true);
  };

  const handleDeleteBudget = async (id) => {
    if (window.confirm('Apakah Anda yakin ingin menghapus anggaran ini?')) {
      try {
        // await budgetAPI.delete(id);
        setBudgets(budgets.filter(budget => budget.id !== id));
      } catch (err) {
        setError('Gagal menghapus anggaran');
        console.error(err);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (formMode === 'create') {
        const newBudget = {
          id: Date.now(),
          category: formData.category,
          amount: parseFloat(formData.amount),
          spent: 0,
        };
        setBudgets([...budgets, newBudget]);
      } else {
        const updatedBudgets = budgets.map(budget => {
          if (budget.id === selectedBudget.id) {
            return {
              ...budget,
              category: formData.category,
              amount: parseFloat(formData.amount),
            };
          }
          return budget;
        });
        setBudgets(updatedBudgets);
      }
      setShowForm(false);
    } catch (err) {
      setError(`Gagal ${formMode === 'create' ? 'membuat' : 'mengupdate'} anggaran`);
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500"></div>
      </div>
    );
  }

  const totalBudget = budgets.reduce((sum, b) => sum + b.amount, 0);
  const totalSpent = budgets.reduce((sum, b) => sum + b.spent, 0);
  const remainingBudget = totalBudget - totalSpent;

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Anggaran Bulanan</h1>
        <button
          onClick={handleCreateBudget}
          className="bg-emerald-500 text-white py-2 px-4 rounded-md hover:bg-emerald-600 flex items-center"
        >
          <FiPlus className="mr-2" />
          Tambah Anggaran
        </button>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-600 mb-2">Total Anggaran</h3>
          <p className="text-2xl font-bold text-gray-800">Rp {totalBudget.toLocaleString('id-ID')}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-600 mb-2">Total Terpakai</h3>
          <p className="text-2xl font-bold text-gray-800">Rp {totalSpent.toLocaleString('id-ID')}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-gray-600 mb-2">Sisa Anggaran</h3>
          <p className="text-2xl font-bold text-gray-800">Rp {remainingBudget.toLocaleString('id-ID')}</p>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md flex items-center">
          <FiAlertCircle className="mr-2" />
          <span>{error}</span>
        </div>
      )}

      {/* Form */}
      {showForm && (
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h3 className="text-lg font-medium text-gray-800 mb-4">
            {formMode === 'create' ? 'Tambah Anggaran Baru' : 'Edit Anggaran'}
          </h3>
          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label htmlFor="category" className="block text-gray-700 mb-2">Kategori</label>
                <select
                  name="category"
                  value={formData.category}
                  onChange={handleInputChange}
                  required
                  className="w-full border border-gray-300 px-3 py-2 rounded-md focus:ring-emerald-500 focus:outline-none"
                >
                  <option value="">Pilih Kategori</option>
                  {categories.map(cat => (
                    <option key={cat.id} value={cat.name}>{cat.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label htmlFor="amount" className="block text-gray-700 mb-2">Jumlah Anggaran</label>
                <input
                  name="amount"
                  type="number"
                  min="0"
                  value={formData.amount}
                  onChange={handleInputChange}
                  required
                  className="w-full border border-gray-300 px-3 py-2 rounded-md focus:ring-emerald-500 focus:outline-none"
                />
              </div>
            </div>
            <div className="flex justify-end space-x-2">
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-100"
              >
                Batal
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-emerald-500 text-white rounded-md hover:bg-emerald-600"
              >
                {formMode === 'create' ? 'Simpan' : 'Update'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Budget Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Kategori</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Anggaran</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Terpakai</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Persentase</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Aksi</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {budgets.map(b => {
              const percentage = (b.spent / b.amount) * 100;
              return (
                <tr key={b.id}>
                  <td className="px-6 py-4 text-sm text-gray-900">{b.category}</td>
                  <td className="px-6 py-4 text-sm text-gray-900">Rp {b.amount.toLocaleString('id-ID')}</td>
                  <td className="px-6 py-4 text-sm text-gray-900">Rp {b.spent.toLocaleString('id-ID')}</td>
                  <td className="px-6 py-4 text-sm">
                    <div className="w-full bg-gray-200 rounded-full h-2.5 mb-1">
                      <div
                        className={`h-2.5 rounded-full ${
                          percentage > 90 ? 'bg-red-500' :
                          percentage > 70 ? 'bg-yellow-500' :
                          'bg-emerald-500'
                        }`}
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                    <div className="text-xs text-gray-500">{percentage.toFixed(0)}% terpakai</div>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button onClick={() => handleEditBudget(b)} className="text-emerald-600 hover:text-emerald-800 mr-3">
                      <FiEdit2 />
                    </button>
                    <button onClick={() => handleDeleteBudget(b.id)} className="text-red-500 hover:text-red-700">
                      <FiTrash2 />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {budgets.length === 0 && (
          <div className="py-8 text-center text-gray-500">
            Belum ada anggaran. Klik "Tambah Anggaran" untuk membuat anggaran baru.
          </div>
        )}
      </div>
    </div>
  );
};

export default BudgetPage;
