import type { MatchedKeyword, MissingKeyword } from '../types';

interface KeywordDetailsProps {
  matchedKeywords: MatchedKeyword[];
  missingKeywords: MissingKeyword[];
}

function MatchedKeywordCard({ keyword }: { keyword: MatchedKeyword }) {
  const { keyword: kw, location, context, effectiveness_score, usage_quality, similarity_score } = keyword;
  
  const getEffectivenessColor = (score: number) => {
    if (score >= 0.9) return '#22c55e';
    if (score >= 0.7) return '#eab308';
    return '#ef4444';
  };

  const getEffectivenessLabel = (score: number) => {
    if (score >= 0.9) return 'Excellent';
    if (score >= 0.7) return 'Good';
    if (score >= 0.5) return 'Fair';
    return 'Poor';
  };

  // Validate data before rendering
  if (!kw || typeof kw !== 'string') {
    console.error('Invalid keyword data:', keyword);
    return null;
  }

  const effectivenessColor = getEffectivenessColor(effectiveness_score);

  return (
    <div className="keyword-card matched-keyword">
      <div className="keyword-header">
        <span className="keyword-name">{kw}</span>
        <div className="keyword-badges">
          <span 
            className="badge effectiveness-badge"
            style={{ backgroundColor: effectivenessColor }}
            title={`Effectiveness: ${effectiveness_score.toFixed(2)}`}
          >
            {getEffectivenessLabel(effectiveness_score)} ({(effectiveness_score * 100).toFixed(0)}%)
          </span>
          {similarity_score !== undefined && (
            <span 
              className="badge similarity-badge"
              style={{ backgroundColor: '#3b82f6' }}
              title={`Similarity: ${similarity_score}%`}
            >
              Sim: {similarity_score}%
            </span>
          )}
        </div>
      </div>
      
      <div className="keyword-details">
        <div className="detail-row">
          <span className="detail-icon">📍</span>
          <span className="detail-text">{location}</span>
        </div>
        
        {context && (
          <div className="detail-row">
            <span className="detail-icon">💬</span>
            <span className="detail-text context-text" title={context}>
              {context.length > 80 ? `${context.substring(0, 80)}...` : context}
            </span>
          </div>
        )}
        
        <div className="detail-row">
          <span className="detail-icon">✨</span>
          <span className="detail-text">{usage_quality}</span>
        </div>
      </div>
    </div>
  );
}

function MissingKeywordCard({ keyword }: { keyword: MissingKeyword }) {
  const { keyword: kw, reason, priority_impact, suggested_location } = keyword;
  
  // Validate data before rendering
  if (!kw || typeof kw !== 'string') {
    console.error('Invalid missing keyword data:', keyword);
    return null;
  }
  
  const getPriorityColor = (impact: string) => {
    switch (impact?.toLowerCase()) {
      case 'high': return '#ef4444';
      case 'medium': return '#eab308';
      case 'low': return '#22c55e';
      default: return '#6b7280';
    }
  };

  return (
    <div className="keyword-card missing-keyword">
      <div className="keyword-header">
        <span className="keyword-name">{kw}</span>
        <span 
          className="badge priority-badge"
          style={{ backgroundColor: getPriorityColor(priority_impact) }}
        >
          {priority_impact.charAt(0).toUpperCase() + priority_impact.slice(1)} Priority
        </span>
      </div>
      
      <div className="keyword-details">
        <div className="detail-row">
          <span className="detail-icon">❌</span>
          <span className="detail-text">{reason}</span>
        </div>
        
        <div className="detail-row">
          <span className="detail-icon">💡</span>
          <span className="detail-text">
            <strong>Suggested:</strong> {suggested_location}
          </span>
        </div>
      </div>
    </div>
  );
}

export default function KeywordDetails({ matchedKeywords, missingKeywords }: KeywordDetailsProps) {
  return (
    <div className="keyword-details-container">
      {matchedKeywords.length > 0 && (
        <div className="keyword-section matched-section">
          <h4 className="section-title">
            ✅ Matched Keywords ({matchedKeywords.length})
          </h4>
          <div className="keyword-grid">
            {matchedKeywords.map((keyword, index) => (
              <MatchedKeywordCard key={index} keyword={keyword} />
            ))}
          </div>
        </div>
      )}
      
      {missingKeywords.length > 0 && (
        <div className="keyword-section missing-section">
          <h4 className="section-title">
            ❌ Missing Keywords ({missingKeywords.length})
          </h4>
          <div className="keyword-grid">
            {missingKeywords.map((keyword, index) => (
              <MissingKeywordCard key={index} keyword={keyword} />
            ))}
          </div>
        </div>
      )}
      
      {matchedKeywords.length === 0 && missingKeywords.length === 0 && (
        <div className="no-keywords">
          <p>No keyword data available</p>
        </div>
      )}
    </div>
  );
}