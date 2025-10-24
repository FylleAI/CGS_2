import React from 'react';
import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';

interface FylleCardProps {
  category: 'company' | 'audience' | 'voice' | 'insight';
  children: React.ReactNode;
  className?: string;
  onMouseEnter?: () => void;
  onMouseLeave?: () => void;
}

const categoryColors = {
  company: 'from-emerald-500/10 to-emerald-600/5 border-emerald-500/20 hover:border-emerald-500/40 hover:shadow-emerald-200/20',
  audience: 'from-blue-500/10 to-blue-600/5 border-blue-500/20 hover:border-blue-500/40 hover:shadow-blue-200/20',
  voice: 'from-purple-500/10 to-purple-600/5 border-purple-500/20 hover:border-purple-500/40 hover:shadow-purple-200/20',
  insight: 'from-amber-500/10 to-amber-600/5 border-amber-500/20 hover:border-amber-500/40 hover:shadow-amber-200/20',
};

export const FylleCard: React.FC<FylleCardProps> = ({
  category,
  children,
  className = '',
  onMouseEnter,
  onMouseLeave
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, ease: 'easeOut' }}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      className={`
        relative overflow-hidden rounded-2xl border bg-gradient-to-br
        ${categoryColors[category]}
        backdrop-blur-sm transition-all duration-200 hover:shadow-lg
        ${className}
      `}
    >
      {children}
    </motion.div>
  );
};

interface CardHeaderProps {
  icon: LucideIcon;
  title: string;
  subtitle?: string;
  confidence?: number;
  category: 'company' | 'audience' | 'voice' | 'insight';
}

const categoryIconColors = {
  company: 'text-emerald-600',
  audience: 'text-blue-600',
  voice: 'text-purple-600',
  insight: 'text-amber-600',
};

export const CardHeader: React.FC<CardHeaderProps> = ({
  icon: Icon,
  title,
  subtitle,
  confidence,
  category,
}) => {
  const getConfidenceLabel = (conf: number) => {
    if (conf >= 0.85) return { label: 'AI confident', color: 'text-emerald-600', emoji: '🧠' };
    if (conf >= 0.6) return { label: 'Under review', color: 'text-amber-600', emoji: '⚙️' };
    return { label: 'Low confidence', color: 'text-red-600', emoji: '🧩' };
  };

  const confidenceInfo = confidence ? getConfidenceLabel(confidence) : null;

  return (
    <div className="p-6 pb-4">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className={`rounded-lg bg-white/50 p-2 ${categoryIconColors[category]}`}>
            <Icon className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
            {subtitle && <p className="text-sm text-gray-600">{subtitle}</p>}
          </div>
        </div>
        {confidenceInfo && (
          <div className="flex items-center gap-1 text-xs">
            <span>{confidenceInfo.emoji}</span>
            <span className={`font-medium ${confidenceInfo.color}`}>
              {confidenceInfo.label}
            </span>
          </div>
        )}
      </div>
      {confidence && (
        <div className="mt-3 h-1 w-full overflow-hidden rounded-full bg-gray-200">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${confidence * 100}%` }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className={`h-full ${
              confidence >= 0.85
                ? 'bg-emerald-500'
                : confidence >= 0.6
                ? 'bg-amber-500'
                : 'bg-red-500'
            }`}
          />
        </div>
      )}
    </div>
  );
};

interface CardContentProps {
  children: React.ReactNode;
  className?: string;
}

export const CardContent: React.FC<CardContentProps> = ({ children, className = '' }) => {
  return <div className={`px-6 py-4 ${className}`}>{children}</div>;
};

interface CardFooterProps {
  children: React.ReactNode;
  className?: string;
}

export const CardFooter: React.FC<CardFooterProps> = ({ children, className = '' }) => {
  return (
    <div className={`border-t border-gray-200/50 bg-white/30 px-6 py-4 ${className}`}>
      {children}
    </div>
  );
};

interface ChipProps {
  children: React.ReactNode;
  variant?: 'default' | 'primary' | 'secondary';
  className?: string;
}

export const Chip: React.FC<ChipProps> = ({ children, variant = 'default', className = '' }) => {
  const variants = {
    default: 'bg-gray-100 text-gray-700 border-gray-200',
    primary: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    secondary: 'bg-blue-50 text-blue-700 border-blue-200',
  };

  return (
    <span
      className={`
        inline-flex items-center rounded-full border px-3 py-1 text-sm font-medium
        ${variants[variant]}
        ${className}
      `}
    >
      {children}
    </span>
  );
};

interface ConfidenceBadgeProps {
  confidence: number;
  source?: string;
}

export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({ confidence, source }) => {
  const percentage = Math.round(confidence * 100);
  const color =
    confidence >= 0.85 ? 'emerald' : confidence >= 0.6 ? 'amber' : 'red';

  return (
    <div className="flex items-center gap-2 text-xs text-gray-600">
      <div className="flex items-center gap-1">
        <div className={`h-2 w-2 rounded-full bg-${color}-500`} />
        <span className="font-medium">{percentage}% confidence</span>
      </div>
      {source && <span className="text-gray-400">• {source}</span>}
    </div>
  );
};

interface SectionProps {
  title: string;
  icon?: LucideIcon;
  children: React.ReactNode;
  className?: string;
}

export const Section: React.FC<SectionProps> = ({ title, icon: Icon, children, className = '' }) => {
  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex items-center gap-2">
        {Icon && <Icon className="h-4 w-4 text-gray-500" />}
        <h4 className="text-sm font-semibold text-gray-700">{title}</h4>
      </div>
      {children}
    </div>
  );
};

