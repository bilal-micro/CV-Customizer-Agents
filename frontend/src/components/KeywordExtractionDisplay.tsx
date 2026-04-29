import type { ExtractedKeyword } from '../types';

interface KeywordExtractionDisplayProps {
  items: ExtractedKeyword[];
  label: string;
  category?: string;
}

function getPriorityIcon(priority: number): string {
  if (priority >= 8) return '🔴';  // Critical (8-10)
  if (priority >= 5) return '🟡';  // Important (5-7)
  return '🟢';  // Nice to have (1-4)
}

function getPriorityLabel(priority: number): string {
  if (priority >= 8) return 'Critical';
  if (priority >= 5) return 'Important';
  return 'Nice to have';
}

function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.9) return '#22c55e';  // Green
  if (confidence >= 0.7) return '#eab308';  // Yellow
  return '#ef4444';  // Red
}

function getCategoryIcon(category: string): string {
  const categoryIcons: Record<string, string> = {
    programming_language: '💻',
    framework: '🔧',
    database: '🗄️',
    devops: '🚀',
    testing: '🧪',
    interpersonal: '🤝',
    leadership: '👑',
    communication: '💬',
    critical_thinking: '🧠',
    productivity: '⏱️',
    flexibility: '🔄',
    education: '🎓',
    certification: '📜',
    experience: '💼',
    tools: '🛠️',
    domain_knowledge: '📚',
    soft_skills: '💡',
    hard_skills: '⚡',
  };
  return categoryIcons[category] || '🏷️';
}

function getKeywordText(item: ExtractedKeyword): string {
  return item.skill || item.keyword || item.item || item.qualification || 'Unknown';
}

function KeywordCard({ item, category }: { item: ExtractedKeyword; category?: string }) {
  const keywordText = getKeywordText(item);
  const priorityIcon = getPriorityIcon(item.priority);
  const priorityLabel = getPriorityLabel(item.priority);
  const confidenceColor = getConfidenceColor(item.confidence);
  const categoryIcon = getCategoryIcon(item.category);
  
  return (
    <div className={`keyword-card ${category ? `category-${category}` : ''}`}>
      <div className="keyword-header">
        <span className="keyword-name">{keywordText}</span>
        <span className="keyword-priority" title={`Priority: ${item.priority}/10 - ${priorityLabel}`}>
          {priorityIcon} {item.priority}/10
        </span>
      </div>
      
      <div className="keyword-metadata">
        <div className="metadata-item">
          <span className="metadata-icon">{categoryIcon}</span>
          <span className="metadata-label">Category:</span>
          <span className="metadata-value">{item.category}</span>
        </div>
        
        <div className="metadata-item">
          <span className="metadata-icon">📊</span>
          <span className="metadata-label">Confidence:</span>
          <span 
            className="metadata-value confidence-bar" 
            style={{ color: confidenceColor }}
          >
            {Math.round(item.confidence * 100)}%
          </span>
          <div 
            className="confidence-track"
            title={`${Math.round(item.confidence * 100)}% confidence`}
          >
            <div 
              className="confidence-fill" 
              style={{ 
                width: `${item.confidence * 100}%`,
                backgroundColor: confidenceColor
              }}
            />
          </div>
        </div>
        
        {item.placement_hints && item.placement_hints.length > 0 && (
          <div className="metadata-item placement-hints">
            <span className="metadata-icon">💡</span>
            <span className="metadata-label">Suggested:</span>
            <div className="placement-tags">
              {item.placement_hints.map((hint, idx) => (
                <span key={idx} className="placement-tag">
                  {hint}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function KeywordExtractionDisplay({ items, label, category }: KeywordExtractionDisplayProps) {
  if (!items || items.length === 0) {
    return null;
  }

  // Sort by priority (highest first)
  const sortedItems = [...items].sort((a, b) => b.priority - a.priority);

  return (
    <div className="keyword-extraction-section">
      <h5 className="section-title">{label}</h5>
      <div className="keyword-cards">
        {sortedItems.map((item, index) => (
          <KeywordCard key={index} item={item} category={category} />
        ))}
      </div>
    </div>
  );
}