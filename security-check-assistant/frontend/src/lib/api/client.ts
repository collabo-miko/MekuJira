/**
 * API client for backend communication
 */

const API_BASE = '/api';

export interface Session {
	id: string;
	filename: string;
	vendor_name: string | null;
	status: string;
	error_message: string | null;
	total_questions: number;
	answered_questions: number;
	confidence_threshold: number;
	created_at: string;
	updated_at: string;
	question_column: string | null;
	answer_column: string | null;
	remarks_column: string | null;
	header_row: number | null;
}

export interface Question {
	id: string;
	session_id: string;
	row_number: number;
	question_text: string;
	remarks: string | null;
	answer_column: string;
	question_type: string;
	choices: string[] | null;
	created_at: string;
}

export interface Answer {
	id: string;
	question_id: string;
	answer_text: string;
	confidence_score: number;
	status: string;
	sources: AnswerSource[];
	original_answer: string | null;
	modified_by_user: boolean;
	created_at: string;
	updated_at: string;
}

export interface AnswerSource {
	type: string;
	document_id?: string;
	document_name?: string;
	page_number?: number;
	snippet?: string;
	knowledge_id?: string;
}

export interface Document {
	id: string;
	pageindex_doc_id: string | null;
	filename: string;
	page_count: number | null;
	status: string;
	error_message: string | null;
	indexed_at: string | null;
	created_at: string;
}

export interface ReviewItem {
	question_id: string;
	row_number: number;
	question_text: string;
	remarks: string | null;
	answer_id: string | null;
	answer_text: string;
	confidence_score: number;
	confidence_level: string;
	status: string;
	sources: AnswerSource[];
}

export interface ReviewResponse {
	session_id: string;
	filename: string;
	vendor_name: string | null;
	total_questions: number;
	items: ReviewItem[];
}

export interface ReportSummary {
	session_id: string;
	filename: string;
	vendor_name: string | null;
	total_questions: number;
	answered_count: number;
	high_confidence_count: number;
	medium_confidence_count: number;
	low_confidence_count: number;
	approved_count: number;
	modified_count: number;
	pending_count: number;
}

export interface DifficultQuestion {
	question_id: string;
	row_number: number;
	question_text: string;
	confidence_score: number;
	reason: string;
}

export interface Report {
	summary: ReportSummary;
	difficult_questions: DifficultQuestion[];
	knowledge_count: number;
}

async function handleResponse<T>(response: Response): Promise<T> {
	if (!response.ok) {
		const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
		throw new Error(error.detail || `HTTP ${response.status}`);
	}
	return response.json();
}

// Excel API
export async function uploadExcel(
	file: File,
	vendorName?: string,
	confidenceThreshold?: number
): Promise<Session> {
	const formData = new FormData();
	formData.append('file', file);
	if (vendorName) formData.append('vendor_name', vendorName);
	if (confidenceThreshold !== undefined) {
		formData.append('confidence_threshold', confidenceThreshold.toString());
	}

	const response = await fetch(`${API_BASE}/excel/upload`, {
		method: 'POST',
		body: formData
	});
	return handleResponse(response);
}

export async function getSessions(): Promise<Session[]> {
	const response = await fetch(`${API_BASE}/excel/sessions`);
	return handleResponse(response);
}

export async function getSession(sessionId: string): Promise<Session> {
	const response = await fetch(`${API_BASE}/excel/sessions/${sessionId}`);
	return handleResponse(response);
}

export async function getSessionQuestions(sessionId: string): Promise<Question[]> {
	const response = await fetch(`${API_BASE}/excel/sessions/${sessionId}/questions`);
	return handleResponse(response);
}

// Documents API
export async function uploadDocument(file: File): Promise<Document> {
	const formData = new FormData();
	formData.append('file', file);

	const response = await fetch(`${API_BASE}/documents/upload`, {
		method: 'POST',
		body: formData
	});
	return handleResponse(response);
}

export async function getDocuments(): Promise<Document[]> {
	const response = await fetch(`${API_BASE}/documents`);
	return handleResponse(response);
}

export async function getDocumentStatus(documentId: string): Promise<Document> {
	const response = await fetch(`${API_BASE}/documents/${documentId}/status`);
	return handleResponse(response);
}

export async function deleteDocument(documentId: string): Promise<void> {
	const response = await fetch(`${API_BASE}/documents/${documentId}`, {
		method: 'DELETE'
	});
	if (!response.ok) {
		const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
		throw new Error(error.detail || `HTTP ${response.status}`);
	}
}

// Answer API
export async function generateAnswers(
	sessionId: string,
	confidenceThreshold?: number
): Promise<{ session_id: string; status: string; message: string }> {
	const response = await fetch(`${API_BASE}/answer/generate`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({
			session_id: sessionId,
			confidence_threshold: confidenceThreshold
		})
	});
	return handleResponse(response);
}

export async function getGenerationStatus(
	sessionId: string
): Promise<{
	session_id: string;
	status: string;
	total_questions: number;
	generated_answers: number;
	answered_questions: number;
	error_message: string | null;
}> {
	const response = await fetch(`${API_BASE}/answer/status/${sessionId}`);
	return handleResponse(response);
}

export async function regenerateAnswer(questionId: string): Promise<Answer> {
	const response = await fetch(`${API_BASE}/answer/regenerate/${questionId}`, {
		method: 'POST'
	});
	return handleResponse(response);
}

// Review API
export async function getReviewItems(sessionId: string): Promise<ReviewResponse> {
	const response = await fetch(`${API_BASE}/review/${sessionId}`);
	return handleResponse(response);
}

export async function approveAnswer(answerId: string): Promise<Answer> {
	const response = await fetch(`${API_BASE}/review/${answerId}/approve`, {
		method: 'PUT'
	});
	return handleResponse(response);
}

export async function modifyAnswer(answerId: string, answerText: string): Promise<Answer> {
	const response = await fetch(`${API_BASE}/review/${answerId}/modify`, {
		method: 'PUT',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ answer_text: answerText })
	});
	return handleResponse(response);
}

export async function finalizeSession(
	sessionId: string
): Promise<{ message: string; knowledge_items_created: number }> {
	const response = await fetch(`${API_BASE}/review/${sessionId}/finalize`, {
		method: 'POST'
	});
	return handleResponse(response);
}

// Report API
export async function getReport(sessionId: string): Promise<Report> {
	const response = await fetch(`${API_BASE}/report/${sessionId}`);
	return handleResponse(response);
}

export function getExportUrl(sessionId: string): string {
	return `${API_BASE}/export/${sessionId}/excel`;
}

export async function getSessionFile(sessionId: string): Promise<File> {
	const response = await fetch(`${API_BASE}/excel/sessions/${sessionId}/file`);
	if (!response.ok) {
		const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
		throw new Error(error.detail || `HTTP ${response.status}`);
	}
	const blob = await response.blob();
	const contentDisposition = response.headers.get('Content-Disposition');
	let filename = 'download.xlsx';
	if (contentDisposition) {
		const match = contentDisposition.match(/filename="?([^";\n]+)"?/);
		if (match) {
			filename = match[1];
		}
	}
	return new File([blob], filename, { type: blob.type });
}
