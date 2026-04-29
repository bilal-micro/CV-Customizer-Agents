import type { StageResult, MatchedKeyword, MissingKeyword, ExtractedKeyword } from '../types';
import KeywordDetails from './KeywordDetails';
import KeywordExtractionDisplay from './KeywordExtractionDisplay';

const STAGE_LABELS: Record<string, string> = {
  keyword_extraction: 'Keyword Extraction',
  cv_matching: 'CV Matching',
  cv_update: 'CV Update',
  ats_rating: 'ATS Rating',
};

const STAGE_ICONS: Record<string, string> = {
  keyword_extraction: '🔍',
  cv_matching: '🎯',
  cv_update: '✏️',
  ats_rating: '📊',
};

const STATUS_ICONS: Record<string, string> = {
  pending: '⏳',
  running: '🔄',
  completed: '✅',
  failed: '❌',
};

function RatingBar({ value, label }: { value: number | null; label: string }) {
  if (value === null) return null;
  const clamped = Math.min(100, Math.max(0, value));
  const color = clamped >= 75 ? '#22c55e' : clamped >= 50 ? '#eab308' : '#ef4444';
  return (
    <div className="rating-bar">
      <div className="rating-label">{label}: {clamped.toFixed(1)}%</div>
      <div className="rating-track">
        <div className="rating-fill" style={{ 
          width: `${clamped}%`, 
          backgroundColor: color,
          backgroundImage: clamped >= 75 
            ? 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)'
            : clamped >= 50 
            ? 'linear-gradient(135deg, #eab308 0%, #ca8a04 100%)'
            : 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)'
        }} />
      </div>
    </div>
  );
}

type KeywordItem = string | { type: string; level: string };

function KeywordList({ items, label, category }: { items: KeywordItem[]; label: string; category?: string }) {
  if (!items?.length) return null;
  
  const formatKeyword = (item: KeywordItem): string => {
    // Handle strings directly (most common case for strengths/weaknesses)
    if (typeof item === 'string') {
      return item;
    }
    // It's an object - check if it's a valid qualification object
    if (item && typeof item === 'object') {
      const hasType = 'type' in item && item.type && item.type !== 'N/A';
      const hasLevel = 'level' in item && item.level && item.level !== 'N/A';
      
      // Only format as object if it has meaningful type/level properties
      if (hasType && hasLevel) {
        const icon = item.type === 'degree' ? '🎓' : '💼';
        return `${icon} ${item.type}: ${item.level}`;
      }
      // Otherwise, try to convert object to string representation
      return Object.values(item).filter(v => v && v !== 'N/A').join(' ') || String(item);
    }
    // Fallback for any other type
    return String(item);
  };

  try {
    return (
      <div className="keyword-section">
        <h5>{label}</h5>
        <div className="keyword-tags">
          {items.map((item, i) => (
            <span key={i} className={`tag ${category ? `category-${category}` : ''}`}>
              {formatKeyword(item)}
            </span>
          ))}
        </div>
      </div>
    );
  } catch (e) {
    console.error('Error rendering keyword list:', e);
    return null;
  }
}

export default function ProcessTracker({ stages }: { stages: StageResult[] }) {
  const getProgressPercentage = () => {
    if (!stages.length) return 0;
    const completed = stages.filter(s => s.status === 'completed').length;
    const running = stages.filter(s => s.status === 'running').length;
    return Math.round(((completed + running * 0.5) / stages.length) * 100);
  };

  return (
    <div className="process-tracker">
      <h3>
        📈 Analysis Progress
        <span style={{ marginLeft: '12px', fontSize: '16px', fontWeight: 600, color: 'var(--primary)' }}>
          {getProgressPercentage()}%
        </span>
      </h3>
      <div className="stages-timeline">
        {stages.map((stage, index) => (
          <div key={stage.id} className={`stage-card ${stage.status}`}>
            <div className="stage-header">
              <span className="stage-icon">{STAGE_ICONS[stage.stage] || '⚙️'}</span>
              <span className="stage-name">
                {STAGE_LABELS[stage.stage] || stage.stage}
                {index + 1 <= stages.findIndex(s => s.status === 'running') && (
                  <span style={{ marginLeft: '8px', fontSize: '12px', color: 'var(--primary)' }}>
                    (Step {index + 1} of {stages.length})
                  </span>
                )}
              </span>
              <span className={`stage-status badge-${stage.status}`}>
                {STATUS_ICONS[stage.status]} {stage.status}
              </span>
            </div>

            {stage.rating !== null && <RatingBar value={stage.rating} label="Stage Quality" />}

            {stage.status === 'completed' && stage.result && (
              <div className="stage-details animate-fade-in">
                {stage.stage === 'keyword_extraction' && (
                  <>
                    <KeywordExtractionDisplay items={(stage.result.hard_skills as ExtractedKeyword[]) || []} label="Hard Skills" category="hard-skills" />
                    <KeywordExtractionDisplay items={(stage.result.soft_skills as ExtractedKeyword[]) || []} label="Soft Skills" category="soft-skills" />
                    <KeywordExtractionDisplay items={(stage.result.qualifications as ExtractedKeyword[]) || []} label="Qualifications" category="qualifications" />
                    <KeywordExtractionDisplay items={(stage.result.keywords as ExtractedKeyword[]) || []} label="Keywords" category="keywords" />
                    <KeywordExtractionDisplay items={(stage.result.must_have as ExtractedKeyword[]) || []} label="Must Have" category="must-have" />
                    <KeywordExtractionDisplay items={(stage.result.nice_to_have as ExtractedKeyword[]) || []} label="Nice to Have" category="nice-to-have" />
                    {stage.result.job_notes && (
                      <div className="notes-section">
                        <h5>📋 Job Notes</h5>
                        <p>{stage.result.job_notes as string}</p>
                      </div>
                    )}
                  </>
                )}

                {stage.stage === 'cv_matching' && (
                  <>
                    {/* Section Analysis Display */}
                    {stage.result.section_analysis && (
                      <div style={{ 
                        marginTop: '16px', 
                        padding: '16px', 
                        backgroundColor: 'var(--bg)', 
                        borderRadius: '8px',
                        border: '1px solid var(--border)'
                      }}>
                        <h5 style={{ marginBottom: '12px', color: 'var(--text-h)', fontWeight: 600 }}>
                          📊 Section Analysis
                        </h5>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '12px' }}>
                          {Object.entries(stage.result.section_analysis as Record<string, any>).map(([sectionName, data]: [string, any]) => {
                            if (!data || !data.present) return null;
                            
                            const getSectionIcon = (name: string) => {
                              switch(name) {
                                case 'education': return '🎓';
                                case 'experience': return '💼';
                                case 'skills': return '🔧';
                                case 'projects': return '📁';
                                case 'summary': return '📝';
                                default: return '📄';
                              }
                            };
                            
                            const getRelevanceColor = (relevance: number) => {
                              if (relevance >= 80) return '#22c55e';
                              if (relevance >= 60) return '#eab308';
                              return '#ef4444';
                            };
                            
                            return (
                              <div key={sectionName} style={{ 
                                padding: '12px', 
                                backgroundColor: 'var(--surface)', 
                                borderRadius: '6px',
                                border: '1px solid var(--border)'
                              }}>
                                <div style={{ 
                                  display: 'flex', 
                                  alignItems: 'center', 
                                  gap: '8px',
                                  marginBottom: '8px' 
                                }}>
                                  <span style={{ fontSize: '20px' }}>{getSectionIcon(sectionName)}</span>
                                  <strong style={{ 
                                    color: 'var(--text-h)', 
                                    fontSize: '14px',
                                    textTransform: 'capitalize'
                                  }}>
                                    {sectionName}
                                  </strong>
                                  {data.relevance > 0 && (
                                    <span style={{ 
                                      marginLeft: 'auto',
                                      padding: '4px 8px',
                                      borderRadius: '12px',
                                      fontSize: '11px',
                                      fontWeight: 600,
                                      backgroundColor: getRelevanceColor(data.relevance),
                                      color: 'white'
                                    }}>
                                      {data.relevance}%
                                    </span>
                                  )}
                                </div>
                                
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '12px' }}>
                                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                    <span style={{ color: 'var(--text-light)' }}>Keyword Density:</span>
                                    <span style={{ fontWeight: 500 }}>{data.keyword_density}%</span>
                                  </div>
                                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                    <span style={{ color: 'var(--text-light)' }}>Keyword Count:</span>
                                    <span style={{ fontWeight: 500 }}>{data.keyword_count}</span>
                                  </div>
                                </div>
                                
                                {data.top_keywords && data.top_keywords.length > 0 && (
                                  <div style={{ marginTop: '8px' }}>
                                    <div style={{ 
                                      fontSize: '11px', 
                                      color: 'var(--text-light)', 
                                      marginBottom: '4px',
                                      fontWeight: 500 
                                    }}>
                                      Top Keywords:
                                    </div>
                                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                                      {data.top_keywords.slice(0, 5).map((kw: string, idx: number) => (
                                        <span key={idx} style={{ 
                                          padding: '2px 8px',
                                          backgroundColor: 'var(--primary-bg)',
                                          color: 'var(--primary)',
                                          borderRadius: '4px',
                                          fontSize: '11px',
                                          fontWeight: 500
                                        }}>
                                          {kw}
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                )}
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}
                    
                    {/* Check if keywords are objects (new format) or strings (old format) */}
                    {(() => {
                      const matched = stage.result.matched_keywords;
                      const missing = stage.result.missing_keywords;
                      
                      // Determine format and render accordingly
                      const isObjectFormat = Array.isArray(matched) && 
                                         matched.length > 0 && 
                                         typeof matched[0] === 'object';
                      
                      if (isObjectFormat) {
                        try {
                          return (
                            <KeywordDetails 
                              matchedKeywords={(matched as MatchedKeyword[]) || []}
                              missingKeywords={(missing as MissingKeyword[]) || []}
                            />
                          );
                        } catch (error) {
                          console.error('Error rendering KeywordDetails:', error);
                          return (
                            <div style={{ 
                              padding: '12px', 
                              backgroundColor: 'var(--error-bg)', 
                              color: 'var(--error)',
                              borderRadius: '8px' 
                            }}>
                              ⚠️ Error displaying keyword details. Please try refreshing the page.
                            </div>
                          );
                        }
                      } else {
                        return (
                          <>
                            <KeywordList items={(matched as string[]) || []} label="✅ Matched Keywords" category="matched" />
                            <KeywordList items={(missing as string[]) || []} label="❌ Missing Keywords" category="missing" />
                          </>
                        );
                      }
                    })()}
                    
                    <KeywordList items={(stage.result.strengths as string[]) || []} label="💪 Strengths" category="strengths" />
                    <KeywordList items={(stage.result.weaknesses as string[]) || []} label="⚠️ Weaknesses" category="weaknesses" />
                    {stage.result.matching_notes && (
                      <div className="notes-section">
                        <h5>📊 Analysis</h5>
                        {(() => {
                          const notes = stage.result.matching_notes;
                          
                          // Handle array format
                          if (Array.isArray(notes)) {
                            // Determine format type from first item
                            const firstNote = notes[0];
                            const isCategoryFormat = typeof firstNote === 'object' && 'category' in firstNote;
                            const isKeywordFormat = typeof firstNote === 'object' && 'keyword' in firstNote;
                            
                            console.log('matching_notes debug:', {
                              isArray: true,
                              itemCount: notes.length,
                              firstNote,
                              isCategoryFormat,
                              isKeywordFormat,
                              allNotes: notes
                            });
                            
                            // Category-based format (Strengths/Weaknesses/Suggestions)
                            if (isCategoryFormat) {
                              return (
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                                  {notes.map((note: any, idx: number) => {
                                    const category = typeof note === 'object' ? note.category : '';
                                    const noteText = typeof note === 'object' ? note.note : String(note);
                                    
                                    return (
                                      <div key={idx} style={{ 
                                        padding: '8px 12px', 
                                        backgroundColor: category === 'Weaknesses' ? 'var(--error-bg)' : 
                                                        category === 'Suggestions' ? 'var(--warning-bg)' : 'var(--success-bg)',
                                        borderRadius: '6px',
                                        borderLeft: `4px solid ${category === 'Weaknesses' ? 'var(--error)' : 
                                                             category === 'Suggestions' ? 'var(--warning)' : 'var(--success)'}`
                                      }}>
                                        <strong style={{ display: 'block', marginBottom: '4px' }}>
                                          {category === 'Strengths' ? '✅' : category === 'Weaknesses' ? '⚠️' : '💡'} {category}
                                        </strong>
                                        <span style={{ fontSize: '14px', color: 'var(--text)' }}>
                                          {noteText}
                                        </span>
                                      </div>
                                    );
                                  })}
                                </div>
                              );
                            }
                            
                            // Keyword-based format (keyword, placement_hints, confidence)
                            if (isKeywordFormat) {
                              return (
                                <div style={{ display: 'grid', gap: '8px' }}>
                                  {notes.map((note: any, idx: number) => {
                                    const keyword = typeof note === 'object' ? note.keyword : '';
                                    const placementHints = typeof note === 'object' && Array.isArray(note.placement_hints) 
                                      ? note.placement_hints.join(', ') 
                                      : '';
                                    const confidence = typeof note === 'object' && typeof note.confidence === 'number'
                                      ? (note.confidence * 100).toFixed(0) + '%'
                                      : '';
                                    
                                    // Skip rendering if keyword data is invalid
                                    if (!keyword || (typeof keyword === 'string' && keyword.trim() === '')) {
                                      console.warn(`Skipping invalid keyword note at index ${idx}:`, note);
                                      return null;
                                    }
                                    
                                    return (
                                      <div key={idx} style={{ 
                                        padding: '10px 12px', 
                                        backgroundColor: 'var(--surface)', 
                                        borderRadius: '6px',
                                        border: '1px solid var(--border)'
                                      }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                                          <span style={{ fontSize: '16px' }}>💡</span>
                                          <strong style={{ color: 'var(--text-h)', fontSize: '14px' }}>
                                            {keyword}
                                          </strong>
                                          {confidence && (
                                            <span style={{ 
                                              marginLeft: 'auto',
                                              padding: '2px 8px',
                                              borderRadius: '10px',
                                              fontSize: '11px',
                                              fontWeight: 600,
                                              backgroundColor: 'var(--primary-bg)',
                                              color: 'var(--primary)'
                                            }}>
                                              Confidence: {confidence}
                                            </span>
                                          )}
                                        </div>
                                        
                                        {placementHints && (
                                          <div style={{ fontSize: '12px', color: 'var(--text-light)' }}>
                                            <span style={{ fontWeight: 500 }}>Placement Hints:</span> {placementHints}
                                          </div>
                                        )}
                                      </div>
                                    );
                                  }).filter(Boolean)}
                                </div>
                              );
                            }
                            
                            // Fallback for unknown array format
                            return <p>{JSON.stringify(notes)}</p>;
                          } else {
                            // Handle string format
                            try {
                              return <p>{String(notes)}</p>;
                            } catch (error) {
                              console.error('Error rendering matching_notes string:', error);
                              return <p style={{ color: 'var(--error)' }}>Unable to display analysis notes</p>;
                            }
                          }
                        })()}
                      </div>
                    )}
                  </>
                )}

                {stage.stage === 'cv_update' && (
                  <>
                    <KeywordList items={(stage.result.changes_made as string[]) || []} label="✏️ Changes Made" />
                    <KeywordList items={(stage.result.unchangeable_gaps as string[]) || []} label="🚫 Unchangeable Gaps" />
                    {stage.result.update_notes && (
                      <div className="notes-section">
                        <h5>📝 Update Notes</h5>
                        <p>{stage.result.update_notes as string}</p>
                      </div>
                    )}
                  </>
                )}

                {stage.stage === 'ats_rating' && (
                  <>
                    <RatingBar value={(stage.result.ats_score as number) ?? null} label="🎯 ATS Score" />
                    <RatingBar value={(stage.result.recruiter_appeal as number) ?? null} label="👥 Recruiter Appeal" />
                    {stage.result.ats_breakdown && (
                      <div className="breakdown">
                        {Object.entries(stage.result.ats_breakdown as Record<string, number>).map(([k, v]) => (
                          <RatingBar key={k} value={v} label={k.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} />
                        ))}
                      </div>
                    )}
                    <KeywordList items={(stage.result.strong_points as string[]) || []} label="✨ Strong Points" category="strengths" />
                    <KeywordList items={(stage.result.weak_points as string[]) || []} label="⚠️ Weak Points" category="weaknesses" />
                    <KeywordList items={(stage.result.improvement_suggestions as string[]) || []} label="💡 Improvement Suggestions" />
                    <KeywordList items={(stage.result.expected_interview_questions as string[]) || []} label="❓ Expected Interview Questions" />
                    {stage.result.overall_assessment && (
                      <div className="notes-section">
                        <h5>📋 Overall Assessment</h5>
                        <p>{stage.result.overall_assessment as string}</p>
                      </div>
                    )}
                  </>
                )}
              </div>
            )}

            {stage.notes && (
              <div className="stage-notes">
                <strong>📝 Notes:</strong> {stage.notes}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}