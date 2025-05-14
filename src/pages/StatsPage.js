import React, { useState, useEffect } from 'react';
import { FiFilter, FiDownload, FiAlertCircle } from 'react-icons/fi';
import {
  PieChart, Pie, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell
} from 'recharts';
import { statsAPI, categoryAPI } from '../api/api';

// Dummy data
const dummyPieData = [
  { name: 'Makanan', value: 1200000, color: '#1D503A' },
  { name: 'Transportasi', value: 600000, color: '#2A7E5F' },
  { name: 'Hiburan', value: 950000, color: '#3FA47A' },
  { name: 'Belanja', value: 800000, color: '#5BC296' },
  { name: 'Lainnya', value: 250000, color: '#8CD9B3' },
];

const dummyBarData = [
  { name: 'Jan', income: 6000000, expense: 4500000 },
  { name: 'Feb', income: 5800000, expense: 4200000 },
  { name: 'Mar', income: 6200000, expense: 4800000 },
  { name: 'Apr', income: 6500000, expense: 3200000 },
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

const StatsPage = () => {
  const [pieData, setPieData] = useState([]);
  const [barData, setBarData] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [showFilter, setShowFilter] = useState(false);
  const [filters, setFilters] = useState({
    period: 'monthly',
    month: new Date().getMonth() + 1,
    year: new Date().getFullYear(),
    category: 'all',
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        // const statsResponse = await statsAPI.getMonthly(filters.month, filters.year);
        // const categoryResponse = await categoryAPI.getAll();

        setPieData(dummyPieData);
        setBarData(dummyBarData);
        setCategories(dummyCategories);
      } catch (err) {
        setError('Gagal memuat data statistik');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [filters]);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500"></div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Statistik</h1>
        <div className="flex space-x-2">
          <button
            onClick={() => setShowFilter(!showFilter)}
            className="border border-gray-300 bg-white text-gray-700 py-2 px-4 rounded-md hover:bg-gray-50 flex items-center"
          >
            <FiFilter className="mr-2" />
            Filter
          </button>
          <button
            className="border border-gray-300 bg-white text-gray-700 py-2 px-4 rounded-md hover:bg-gray-50 flex items-center"
          >
            <FiDownload className="mr-2" />
            Export
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md flex items-center">
          <FiAlertCircle className="mr-2" />
          <span>{error}</span>
        </div>
      )}

      {/* Filter Form */}
      {showFilter && (
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h3 className="text-lg font-medium text-gray-800 mb-4">Filter Statistik</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
            <div>
              <label className="block text-gray-700 mb-2">Periode</label>
              <select
                name="period"
                value={filters.period}
                onChange={handleFilterChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-emerald-500 focus:outline-none"
              >
                <option value="monthly">Bulanan</option>
                <option value="yearly">Tahunan</option>
              </select>
            </div>

            {filters.period === 'monthly' && (
              <div>
                <label className="block text-gray-700 mb-2">Bulan</label>
                <select
                  name="month"
                  value={filters.month}
                  onChange={handleFilterChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-emerald-500 focus:outline-none"
                >
                  {[
                    'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                    'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
                  ].map((month, index) => (
                    <option key={index} value={index + 1}>{month}</option>
                  ))}
                </select>
              </div>
            )}

            <div>
              <label className="block text-gray-700 mb-2">Tahun</label>
              <select
                name="year"
                value={filters.year}
                onChange={handleFilterChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-emerald-500 focus:outline-none"
              >
                {[2025, 2024, 2023, 2022].map(year => (
                  <option key={year} value={year}>{year}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-gray-700 mb-2">Kategori</label>
              <select
                name="category"
                value={filters.category}
                onChange={handleFilterChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-emerald-500 focus:outline-none"
              >
                <option value="all">Semua Kategori</option>
                {categories.map(cat => (
                  <option key={cat.id} value={cat.name}>{cat.name}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex justify-end">
            <button
              onClick={() => setFilters({
                period: 'monthly',
                month: new Date().getMonth() + 1,
                year: new Date().getFullYear(),
                category: 'all',
              })}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-100 mr-2"
            >
              Reset
            </button>
            <button
              onClick={() => setShowFilter(false)}
              className="px-4 py-2 bg-emerald-500 text-white rounded-md hover:bg-emerald-600"
            >
              Terapkan Filter
            </button>
          </div>
        </div>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Pie Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-800 mb-4">Pengeluaran per Kategori</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => [`Rp ${value.toLocaleString('id-ID')}`, 'Jumlah']} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Bar Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-800 mb-4">Pemasukan vs Pengeluaran</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip formatter={(value) => [`Rp ${value.toLocaleString('id-ID')}`, 'Jumlah']} />
                <Legend />
                <Bar dataKey="income" name="Pemasukan" fill="#1D503A" />
                <Bar dataKey="expense" name="Pengeluaran" fill="#FF6B6B" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Summary Table */}
      <div className="mt-8 bg-white rounded-lg shadow overflow-hidden">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-800">Ringkasan Keuangan</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Kategori</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Anggaran</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Pengeluaran</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Sisa</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Persentase</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {pieData.map((item, index) => {
                const budget = item.value * 1.5;
                const remaining = budget - item.value;
                const percentage = (item.value / budget) * 100;

                return (
                  <tr key={index}>
                    <td className="px-6 py-4 flex items-center">
                      <div className="w-3 h-3 rounded-full mr-2" style={{ backgroundColor: item.color }}></div>
                      <span className="text-sm text-gray-900">{item.name}</span>
                    </td>
                    <td className="px-6 py-4 text-right text-sm text-gray-900">Rp {budget.toLocaleString('id-ID')}</td>
                    <td className="px-6 py-4 text-right text-sm text-gray-900">Rp {item.value.toLocaleString('id-ID')}</td>
                    <td className="px-6 py-4 text-right text-sm text-gray-900">Rp {remaining.toLocaleString('id-ID')}</td>
                    <td className="px-6 py-4 text-right">
                      <div className="text-sm text-gray-900">{percentage.toFixed(0)}%</div>
                      <div className="w-full bg-gray-200 rounded-full h-2.5 mt-1">
                        <div
                          className={`h-2.5 rounded-full ${
                            percentage > 90 ? 'bg-red-500' :
                            percentage > 70 ? 'bg-yellow-500' :
                            'bg-emerald-500'
                          }`}
                          style={{ width: `${percentage}%` }}
                        ></div>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default StatsPage;
