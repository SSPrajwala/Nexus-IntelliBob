import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

export interface PDFExportOptions {
  filename?: string;
  elementId: string;
  title?: string;
  scale?: number;
}

/**
 * Export HTML content to PDF
 * @param options - Configuration options for PDF export
 */
export async function exportToPDF(options: PDFExportOptions): Promise<void> {
  const {
    filename = 'Nexus-IntelliBob-Report.pdf',
    elementId,
    title = 'Nexus-IntelliBob Analysis Report',
    scale = 2,
  } = options;

  try {
    // Get the element to export
    const element = document.getElementById(elementId);
    if (!element) {
      throw new Error(`Element with id "${elementId}" not found`);
    }

    // Show loading state (optional - could be handled by caller)
    const originalCursor = document.body.style.cursor;
    document.body.style.cursor = 'wait';

    // Capture the element as canvas with high quality
    const canvas = await html2canvas(element, {
      scale: scale,
      useCORS: true,
      logging: false,
      backgroundColor: '#0B0F19', // Match dark theme background
      windowWidth: element.scrollWidth,
      windowHeight: element.scrollHeight,
    });

    // Calculate PDF dimensions
    const imgWidth = 210; // A4 width in mm
    const pageHeight = 297; // A4 height in mm
    const imgHeight = (canvas.height * imgWidth) / canvas.width;
    
    // Create PDF
    const pdf = new jsPDF({
      orientation: imgHeight > imgWidth ? 'portrait' : 'portrait',
      unit: 'mm',
      format: 'a4',
    });

    // Add title page metadata
    pdf.setProperties({
      title: title,
      subject: 'AI-Powered Incident Intelligence Analysis',
      author: 'Nexus-IntelliBob',
      creator: 'Nexus-IntelliBob Platform',
    });

    let heightLeft = imgHeight;
    let position = 0;

    // Convert canvas to image
    const imgData = canvas.toDataURL('image/png');

    // Add first page
    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
    heightLeft -= pageHeight;

    // Add additional pages if content is longer than one page
    while (heightLeft > 0) {
      position = heightLeft - imgHeight;
      pdf.addPage();
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;
    }

    // Save the PDF
    pdf.save(filename);

    // Restore cursor
    document.body.style.cursor = originalCursor;

    return Promise.resolve();
  } catch (error) {
    // Restore cursor on error
    document.body.style.cursor = 'default';
    console.error('PDF export failed:', error);
    throw error;
  }
}

/**
 * Generate filename with timestamp
 */
export function generatePDFFilename(prefix: string = 'Nexus-Report'): string {
  const timestamp = new Date().toISOString().split('T')[0];
  return `${prefix}_${timestamp}.pdf`;
}

/**
 * Export specific report types
 */
export const exportReportTypes = {
  scan: (elementId: string) =>
    exportToPDF({
      elementId,
      filename: generatePDFFilename('Nexus-Scan-Report'),
      title: 'Nexus-IntelliBob Risk Scan Report',
    }),

  blastRadius: (elementId: string) =>
    exportToPDF({
      elementId,
      filename: generatePDFFilename('Nexus-Blast-Radius'),
      title: 'Nexus-IntelliBob Blast Radius Analysis',
    }),

  preMortem: (elementId: string) =>
    exportToPDF({
      elementId,
      filename: generatePDFFilename('Nexus-PreMortem'),
      title: 'Nexus-IntelliBob Pre-Mortem Report',
    }),

  timeline: (elementId: string) =>
    exportToPDF({
      elementId,
      filename: generatePDFFilename('Nexus-Timeline'),
      title: 'Nexus-IntelliBob Engineering Timeline',
    }),
};

// Made with Bob
