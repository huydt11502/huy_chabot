import React, { useState, useEffect } from 'react';
import { XMarkIcon, SearchIcon } from './Icons';
import { Disease, ragService } from '../services/ragService';

interface DiseaseSelectorModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectDisease: (disease: Disease) => void;
}

const DiseaseSelectorModal: React.FC<DiseaseSelectorModalProps> = ({
  isOpen,
  onClose,
  onSelectDisease,
}) => {
  const [diseases, setDiseases] = useState<Disease[]>([]);
  const [filteredDiseases, setFilteredDiseases] = useState<Disease[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [error, setError] = useState<string>('');

  const categories = [
    { value: 'all', label: 'Tất cả', color: 'bg-gray-100 text-gray-800' },
    { value: 'pediatrics', label: 'Nhi khoa', color: 'bg-blue-100 text-blue-800' },
    { value: 'treatment', label: 'Phác đồ điều trị', color: 'bg-green-100 text-green-800' },
    { value: 'procedures', label: 'Thủ thuật', color: 'bg-purple-100 text-purple-800' },
  ];

  useEffect(() => {
    if (isOpen) {
      loadDiseases();
    }
  }, [isOpen]);

  useEffect(() => {
    filterDiseases();
  }, [diseases, searchTerm, selectedCategory]);

  const loadDiseases = async () => {
    console.log('[DiseaseSelectorModal] Loading diseases...');
    setIsLoading(true);
    setError('');
    try {
      const data = await ragService.getDiseases();
      console.log('[DiseaseSelectorModal] Loaded diseases:', data.length);
      setDiseases(data);
      setFilteredDiseases(data);
    } catch (err) {
      console.error('[DiseaseSelectorModal] Load error:', err);
      setError('Không thể tải danh sách bệnh. Vui lòng kiểm tra kết nối RAG API.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const filterDiseases = () => {
    let filtered = diseases;

    // Filter by category
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(d => d.category === selectedCategory);
    }

    // Filter by search term
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(d => 
        d.name.toLowerCase().includes(term) ||
        d.sections.some(s => s.toLowerCase().includes(term))
      );
    }

    setFilteredDiseases(filtered);
  };

  const handleSelectDisease = (disease: Disease) => {
    onSelectDisease(disease);
    handleClose();
  };

  const handleClose = () => {
    setSearchTerm('');
    setSelectedCategory('all');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col animate-in fade-in zoom-in duration-200">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-100 bg-gradient-to-r from-primary-50 to-blue-50">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Chọn Ca Bệnh</h2>
            <p className="text-sm text-gray-500 mt-1">
              {filteredDiseases.length} ca bệnh khả dụng
            </p>
          </div>
          <button
            onClick={handleClose}
            className="p-2 hover:bg-white/50 rounded-lg transition-colors"
          >
            <XMarkIcon className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Search and Filter */}
        <div className="p-6 space-y-4 border-b border-gray-100">
          {/* Search */}
          <div className="relative">
            <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Tìm kiếm theo tên bệnh hoặc mục..."
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          {/* Category Filter */}
          <div className="flex flex-wrap gap-2">
            {categories.map(cat => (
              <button
                key={cat.value}
                onClick={() => setSelectedCategory(cat.value)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  selectedCategory === cat.value
                    ? cat.color
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {cat.label}
                {selectedCategory === cat.value && (
                  <span className="ml-2 text-xs">
                    ({filteredDiseases.length})
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Disease List */}
        <div className="flex-1 overflow-y-auto p-6">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">⚠️</span>
              </div>
              <p className="text-red-600 font-medium">{error}</p>
              <button
                onClick={loadDiseases}
                className="mt-4 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
              >
                Thử lại
              </button>
            </div>
          ) : filteredDiseases.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">🔍</span>
              </div>
              <p className="text-gray-600">Không tìm thấy ca bệnh nào</p>
            </div>
          ) : (
            <div className="grid gap-3">
              {filteredDiseases.map(disease => {
                const categoryInfo = categories.find(c => c.value === disease.category);
                return (
                  <button
                    key={disease.id}
                    onClick={() => handleSelectDisease(disease)}
                    className="text-left p-4 border border-gray-200 rounded-xl hover:border-primary-300 hover:bg-primary-50/50 transition-all group"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
                          {disease.name}
                        </h3>
                        {disease.sections && disease.sections.length > 0 && (
                          <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                            {disease.sections.slice(0, 3).join(' • ')}
                            {disease.sections.length > 3 && '...'}
                          </p>
                        )}
                      </div>
                      <span className={`px-2 py-1 rounded-lg text-xs font-medium whitespace-nowrap ${categoryInfo?.color}`}>
                        {categoryInfo?.label}
                      </span>
                    </div>
                    <div className="text-xs text-gray-400 mt-2">
                      Nguồn: {disease.source}
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-100 bg-gray-50">
          <p className="text-sm text-gray-500">
            Chọn ca bệnh để bắt đầu đánh giá
          </p>
          <button
            onClick={handleClose}
            className="px-4 py-2 text-gray-700 hover:bg-gray-200 rounded-lg transition-colors"
          >
            Đóng
          </button>
        </div>
      </div>
    </div>
  );
};

export default DiseaseSelectorModal;
