import React, { useState } from 'react';
import { CaseConfig, CaseType, ClinicalSystem, DifficultyLevel, AgeGroup } from '../types';
import { CLINICAL_SYSTEMS, DIFFICULTY_LEVELS, AGE_GROUPS } from '../constants';
import { XMarkIcon, ShuffleIcon, SettingsIcon, PlayIcon, ChevronRightIcon } from './Icons';

interface CaseTypeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onStartCase: (config: CaseConfig) => void;
}

const CaseTypeModal: React.FC<CaseTypeModalProps> = ({ isOpen, onClose, onStartCase }) => {
  const [step, setStep] = useState<'select' | 'customize'>('select');
  const [config, setConfig] = useState<CaseConfig>({
    caseType: 'random',
  });

  const handleSelectRandom = () => {
    onStartCase({ caseType: 'random' });
    resetAndClose();
  };

  const handleSelectCustomised = () => {
    setStep('customize');
    setConfig({ ...config, caseType: 'customised' });
  };

  const handleStartCustomised = () => {
    // Validate required fields
    if (!config.clinicalSystem) {
      alert('Vui lòng chọn hệ cơ quan lâm sàng');
      return;
    }
    onStartCase(config);
    resetAndClose();
  };

  const resetAndClose = () => {
    setStep('select');
    setConfig({ caseType: 'random' });
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden animate-in fade-in zoom-in duration-200">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-100">
          <div>
            <h2 className="text-xl font-bold text-gray-900">
              {step === 'select' ? 'Bắt đầu ca luyện tập' : 'Tùy chỉnh ca bệnh'}
            </h2>
            <p className="text-sm text-gray-500 mt-1">
              {step === 'select' 
                ? 'Chọn loại ca bệnh bạn muốn luyện tập' 
                : 'Điều chỉnh các thông số cho ca bệnh'}
            </p>
          </div>
          <button
            onClick={resetAndClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <XMarkIcon className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {step === 'select' ? (
            <div className="space-y-4">
              {/* Random Case Option */}
              <button
                onClick={handleSelectRandom}
                className="w-full p-5 bg-gradient-to-br from-primary-50 to-blue-50 border-2 border-primary-200 rounded-xl hover:border-primary-400 hover:shadow-lg transition-all group text-left"
              >
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center group-hover:bg-primary-200 transition-colors">
                    <ShuffleIcon className="w-6 h-6 text-primary-600" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 mb-1 flex items-center gap-2">
                      Ca ngẫu nhiên
                      <span className="text-xs bg-primary-100 text-primary-700 px-2 py-0.5 rounded-full">Khuyến nghị</span>
                    </h3>
                    <p className="text-sm text-gray-600">
                      Hệ thống sẽ tự động chọn ngẫu nhiên một ca bệnh phù hợp với trình độ của bạn
                    </p>
                  </div>
                  <ChevronRightIcon className="w-5 h-5 text-gray-400 group-hover:text-primary-500 transition-colors" />
                </div>
              </button>

              {/* Customised Case Option */}
              <button
                onClick={handleSelectCustomised}
                className="w-full p-5 bg-gray-50 border-2 border-gray-200 rounded-xl hover:border-gray-300 hover:shadow-lg transition-all group text-left"
              >
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-gray-100 rounded-xl flex items-center justify-center group-hover:bg-gray-200 transition-colors">
                    <SettingsIcon className="w-6 h-6 text-gray-600" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 mb-1">Ca tùy chỉnh</h3>
                    <p className="text-sm text-gray-600">
                      Tự chọn hệ cơ quan, độ tuổi và mức độ khó của ca bệnh
                    </p>
                  </div>
                  <ChevronRightIcon className="w-5 h-5 text-gray-400 group-hover:text-gray-500 transition-colors" />
                </div>
              </button>
            </div>
          ) : (
            <div className="space-y-5">
              {/* Clinical System */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Hệ cơ quan lâm sàng <span className="text-red-500">*</span>
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {CLINICAL_SYSTEMS.map((system) => (
                    <button
                      key={system.value}
                      onClick={() => setConfig({ ...config, clinicalSystem: system.value })}
                      className={`p-3 text-sm rounded-lg border-2 transition-all ${
                        config.clinicalSystem === system.value
                          ? 'border-primary-500 bg-primary-50 text-primary-700 font-medium'
                          : 'border-gray-200 hover:border-gray-300 text-gray-700'
                      }`}
                    >
                      {system.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Age Group */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nhóm tuổi
                </label>
                <select
                  value={config.ageGroup || ''}
                  onChange={(e) => setConfig({ ...config, ageGroup: e.target.value as AgeGroup || undefined })}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="">Bất kỳ</option>
                  {AGE_GROUPS.map((age) => (
                    <option key={age.value} value={age.value}>
                      {age.label} ({age.range})
                    </option>
                  ))}
                </select>
              </div>

              {/* Difficulty */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Mức độ khó
                </label>
                <div className="flex gap-2">
                  {DIFFICULTY_LEVELS.map((level) => (
                    <button
                      key={level.value}
                      onClick={() => setConfig({ ...config, difficulty: level.value })}
                      className={`flex-1 p-3 text-sm rounded-lg border-2 transition-all ${
                        config.difficulty === level.value
                          ? 'border-primary-500 bg-primary-50 text-primary-700 font-medium'
                          : 'border-gray-200 hover:border-gray-300 text-gray-700'
                      }`}
                    >
                      <div className="font-medium">{level.label}</div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 pt-0 flex gap-3">
          {step === 'customize' && (
            <>
              <button
                onClick={() => setStep('select')}
                className="flex-1 px-4 py-3 border border-gray-300 rounded-xl text-gray-700 font-medium hover:bg-gray-50 transition-colors"
              >
                Quay lại
              </button>
              <button
                onClick={handleStartCustomised}
                className="flex-1 px-4 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 transition-colors flex items-center justify-center gap-2"
              >
                <PlayIcon className="w-5 h-5" />
                Bắt đầu
              </button>
            </>
          )}
          {step === 'select' && (
            <button
              onClick={resetAndClose}
              className="w-full px-4 py-3 border border-gray-300 rounded-xl text-gray-700 font-medium hover:bg-gray-50 transition-colors"
            >
              Hủy
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default CaseTypeModal;
