import jsPDF from 'jspdf'
import { RecommendationResponse } from '@/types/api'

/**
 * Client-side PDF export utility (BACKUP/RESTORED)
 * 
 * Note: This is a backup/fallback option. The main PDF export now uses
 * the backend service at /api/v1/pdf/encounter/{encounter_id}/pdf
 * which supports:
 * - Multi-component recommendations
 * - Bangla font rendering
 * - Better formatting
 * 
 * This client-side version is kept for:
 * - Offline fallback
 * - Reference implementation
 * - Alternative export option
 */
export function exportToPDF(recommendation: RecommendationResponse) {
  const doc = new jsPDF()
  
  // Title
  doc.setFontSize(18)
  doc.text('Blood Transfusion Recommendation', 20, 20)
  
  // Disclaimer
  doc.setFontSize(9)
  doc.setTextColor(102, 102, 102)
  doc.text(
    'Clinical decision support only. Confirm with local hospital policy and clinical judgment.',
    20,
    30
  )
  
  let yPos = 40
  
  // Multi-component recommendations
  if (recommendation.components && recommendation.components.length > 0) {
    recommendation.components.forEach((comp, index) => {
      if (yPos > 250) {
        doc.addPage()
        yPos = 20
      }
      
      // Component header
      doc.setFontSize(14)
      doc.setTextColor(0, 0, 0)
      doc.text(
        `Component ${index + 1}: ${comp.component || 'No transfusion recommended'}`,
        20,
        yPos
      )
      yPos += 10
      
      // Action (recommend/contraindicate)
      if (comp.action === 'contraindicate') {
        doc.setFontSize(12)
        doc.setTextColor(200, 0, 0)
        doc.text('CONTRAINDICATION:', 20, yPos)
        yPos += 7
      }
      
      // Dose
      if (comp.component && comp.action === 'recommend') {
        doc.setFontSize(12)
        doc.setTextColor(0, 0, 0)
        doc.text('Dose:', 20, yPos)
        doc.text(comp.dose_text, 20, yPos + 7)
        yPos += 15
        
        if (comp.units) {
          doc.setFontSize(10)
          doc.text(
            `Units: ${comp.units} | Volume: ${comp.volume_ml || 'N/A'} mL`,
            20,
            yPos
          )
          yPos += 7
        }
        
        // Expected Increment
        doc.setFontSize(12)
        doc.text('Expected Increment:', 20, yPos)
        doc.text(comp.expected_increment, 20, yPos + 7)
        yPos += 12
      }
      
      // Rationale
      doc.setFontSize(12)
      doc.text('Rationale:', 20, yPos)
      yPos += 7
      doc.setFontSize(10)
      comp.why.forEach((point) => {
        doc.text(`• ${point}`, 20, yPos)
        yPos += 6
        if (yPos > 250) {
          doc.addPage()
          yPos = 20
        }
      })
      yPos += 5
      
      // Recheck Plan
      doc.setFontSize(12)
      doc.text('Recheck Plan:', 20, yPos)
      doc.setFontSize(10)
      doc.text(comp.recheck_plan, 20, yPos + 7)
      yPos += 15
      
      // Warnings
      if (comp.warnings.length > 0) {
        doc.setFontSize(12)
        doc.text('Warnings:', 20, yPos)
        doc.setFontSize(10)
        yPos += 7
        comp.warnings.forEach((warning) => {
          doc.text(`⚠ ${warning}`, 20, yPos)
          yPos += 6
          if (yPos > 250) {
            doc.addPage()
            yPos = 20
          }
        })
        yPos += 5
      }
      
      // References
      if (comp.references.length > 0) {
        doc.setFontSize(12)
        doc.text('References:', 20, yPos)
        doc.setFontSize(10)
        yPos += 7
        comp.references.forEach((ref) => {
          doc.text(`• ${ref}`, 20, yPos)
          yPos += 6
          if (yPos > 250) {
            doc.addPage()
            yPos = 20
          }
        })
        yPos += 10
      }
      
      // Separator between components
      if (index < recommendation.components.length - 1) {
        doc.setDrawColor(200, 200, 200)
        doc.line(20, yPos, 190, yPos)
        yPos += 10
      }
    })
  } else {
    // Fallback for old single-component format (if still exists)
    doc.setFontSize(14)
    doc.setTextColor(0, 0, 0)
    doc.text('Component:', 20, yPos)
    doc.setFontSize(12)
    doc.text('No transfusion recommended', 20, yPos + 7)
    yPos += 15
  }
  
  // Overall warnings (MTP, etc.)
  if (recommendation.overall_warnings && recommendation.overall_warnings.length > 0) {
    doc.setFontSize(14)
    doc.setTextColor(200, 100, 0)
    doc.text('Overall Warnings:', 20, yPos)
    doc.setFontSize(10)
    yPos += 7
    recommendation.overall_warnings.forEach((warning) => {
      doc.text(`⚠ ${warning}`, 20, yPos)
      yPos += 6
      if (yPos > 250) {
        doc.addPage()
        yPos = 20
      }
    })
    yPos += 10
  }
  
  // MTP Protocol indicator
  if (recommendation.mtp_protocol) {
    doc.setFontSize(12)
    doc.setTextColor(200, 0, 0)
    doc.text('⚠ MASSIVE TRANSFUSION PROTOCOL (MTP) CONTEXT', 20, yPos)
    yPos += 10
  }
  
  // Rule IDs and Version
  yPos += 5
  doc.setFontSize(10)
  doc.setTextColor(102, 102, 102)
  const allRuleIds = recommendation.components
    ? recommendation.components.flatMap(c => c.rule_ids || [])
    : []
  if (allRuleIds.length > 0) {
    doc.text(`Rule IDs: ${[...new Set(allRuleIds)].join(', ')}`, 20, yPos)
  }
  doc.text(`Rule Version: ${recommendation.rule_version}`, 20, yPos + 7)
  
  // Save
  doc.save('transfusion-recommendation.pdf')
}
