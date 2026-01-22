// frontend/components/CardioIQRecommendationCard.tsx

'use client'

import { CardioIQOutput } from '@/types/cardioiq'
import { Heart, AlertTriangle, CheckCircle, Info, BookOpen, TrendingUp, DollarSign } from 'lucide-react'

interface CardioIQRecommendationCardProps {
  recommendation: CardioIQOutput
}

export default function CardioIQRecommendationCard({ recommendation }: CardioIQRecommendationCardProps) {
  // Determine severity color based on clinical category
  const getSeverityColor = (category: string) => {
    if (category.includes('STEMI')) return 'red'
    if (category.includes('NSTEMI')) return 'orange'
    if (category.includes('Low Risk')) return 'green'
    return 'blue'
  }

  const severityColor = getSeverityColor(recommendation.clinical_category)
  const colorClasses = {
    red: {
      bg: 'bg-red-50',
      border: 'border-red-200',
      text: 'text-red-800',
      icon: 'text-red-600'
    },
    orange: {
      bg: 'bg-orange-50',
      border: 'border-orange-200',
      text: 'text-orange-800',
      icon: 'text-orange-600'
    },
    green: {
      bg: 'bg-green-50',
      border: 'border-green-200',
      text: 'text-green-800',
      icon: 'text-green-600'
    },
    blue: {
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      text: 'text-blue-800',
      icon: 'text-blue-600'
    }
  }

  const colors = colorClasses[severityColor]

  return (
    <div className="space-y-6">
      {/* Clinical Category */}
      <div className={`p-6 ${colors.bg} border-l-4 ${colors.border} rounded-md`}>
        <div className="flex items-start space-x-3">
          <Heart className={`h-6 w-6 ${colors.icon} mt-1`} />
          <div className="flex-1">
            <h3 className={`text-lg font-semibold ${colors.text} mb-2`}>
              {recommendation.clinical_category}
            </h3>
            <p className={`text-sm ${colors.text}`}>
              Recommended Level of Care: <span className="font-semibold">{recommendation.recommended_level_of_care}</span>
            </p>
          </div>
        </div>
      </div>

      {/* Risk Scores */}
      {recommendation.risk_scores && recommendation.risk_scores.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
          <div className="flex items-center space-x-2 mb-4">
            <TrendingUp className="h-5 w-5 text-gray-600" />
            <h4 className="font-semibold text-gray-800">Risk Scores</h4>
          </div>
          <div className="space-y-3">
            {recommendation.risk_scores.map((score, idx) => (
              <div key={idx} className="flex items-center justify-between">
                <span className="text-sm text-gray-700">{score.score_name}</span>
                <div className="flex items-center space-x-3">
                  <span className="text-sm font-semibold text-gray-900">{score.value}</span>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    score.risk_category === 'low' ? 'bg-green-100 text-green-800' :
                    score.risk_category === 'intermediate' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {score.risk_category.toUpperCase()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommended Actions */}
      {recommendation.recommended_actions && recommendation.recommended_actions.length > 0 && (
        <div className="bg-white rounded-lg p-6 border border-gray-200">
          <div className="flex items-center space-x-2 mb-4">
            <CheckCircle className="h-5 w-5 text-blue-600" />
            <h4 className="font-semibold text-gray-800">Recommended Actions</h4>
          </div>
          <ul className="space-y-2">
            {recommendation.recommended_actions.map((action, idx) => (
              <li key={idx} className="flex items-start space-x-2">
                <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                <span className="text-sm text-gray-700">{action}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Safety Warnings */}
      {recommendation.safety_warnings && recommendation.safety_warnings.length > 0 && (
        <div className="bg-yellow-50 rounded-lg p-6 border-l-4 border-yellow-400">
          <div className="flex items-center space-x-2 mb-4">
            <AlertTriangle className="h-5 w-5 text-yellow-600" />
            <h4 className="font-semibold text-yellow-800">Safety Warnings</h4>
          </div>
          <ul className="space-y-2">
            {recommendation.safety_warnings.map((warning, idx) => (
              <li key={idx} className="flex items-start space-x-2">
                <div className="w-1.5 h-1.5 bg-yellow-600 rounded-full mt-2 flex-shrink-0"></div>
                <span className="text-sm text-yellow-800">{warning}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Cost Flags */}
      {recommendation.cost_flags && recommendation.cost_flags.length > 0 && (
        <div className="bg-green-50 rounded-lg p-6 border-l-4 border-green-400">
          <div className="flex items-center space-x-2 mb-4">
            <DollarSign className="h-5 w-5 text-green-600" />
            <h4 className="font-semibold text-green-800">Cost Optimization</h4>
          </div>
          <ul className="space-y-2">
            {recommendation.cost_flags.map((flag, idx) => (
              <li key={idx} className="flex items-start space-x-2">
                <div className="w-1.5 h-1.5 bg-green-600 rounded-full mt-2 flex-shrink-0"></div>
                <span className="text-sm text-green-800">{flag}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Rationale */}
      {recommendation.rationale_summary && recommendation.rationale_summary.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
          <div className="flex items-center space-x-2 mb-4">
            <Info className="h-5 w-5 text-gray-600" />
            <h4 className="font-semibold text-gray-800">Clinical Rationale</h4>
          </div>
          <ul className="space-y-2">
            {recommendation.rationale_summary.map((rationale, idx) => (
              <li key={idx} className="flex items-start space-x-2">
                <div className="w-1.5 h-1.5 bg-gray-500 rounded-full mt-2 flex-shrink-0"></div>
                <span className="text-sm text-gray-700">{rationale}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Guidelines */}
      {recommendation.guideline_links && recommendation.guideline_links.length > 0 && (
        <div className="bg-blue-50 rounded-lg p-6 border border-blue-200">
          <div className="flex items-center space-x-2 mb-4">
            <BookOpen className="h-5 w-5 text-blue-600" />
            <h4 className="font-semibold text-blue-800">Guideline References</h4>
          </div>
          <div className="flex flex-wrap gap-2">
            {recommendation.guideline_links.map((guideline, idx) => (
              <span key={idx} className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                {guideline}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Rule Info */}
      <div className="text-xs text-gray-500 pt-4 border-t border-gray-200">
        <p>Rules triggered: {recommendation.rule_hits.join(', ')}</p>
      </div>
    </div>
  )
}
