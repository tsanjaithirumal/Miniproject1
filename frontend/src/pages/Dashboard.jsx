import React, { useState, useEffect } from 'react';
import api from '../api';
import { Upload, Trash2, FileText, Search, Loader2 } from 'lucide-react';

const Dashboard = () => {
    const [documents, setDocuments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [search, setSearch] = useState('');

    useEffect(() => {
        fetchDocuments();
    }, []);

    const fetchDocuments = async () => {
        try {
            const response = await api.get('/documents/');
            setDocuments(response.data);
        } catch (error) {
            console.error('Failed to fetch documents', error);
        } finally {
            setLoading(false);
        }
    };

    const handleUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        setUploading(true);
        try {
            await api.post('/documents/upload', formData);
            fetchDocuments();
        } catch (error) {
            alert('Upload failed');
        } finally {
            setUploading(false);
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm('Are you sure?')) return;
        try {
            await api.delete(`/documents/${id}`);
            setDocuments(documents.filter(doc => doc.id !== id));
        } catch (error) {
            alert('Delete failed');
        }
    };

    const filteredDocs = documents.filter(doc =>
        doc.filename.toLowerCase().includes(search.toLowerCase())
    );

    return (
        <div className="animate-fade-in">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <h1>My Medical Records</h1>
                <label className="btn btn-primary" style={{ cursor: uploading ? 'wait' : 'pointer' }}>
                    {uploading ? <Loader2 className="animate-spin" style={{ marginRight: '0.5rem' }} /> : <Upload style={{ marginRight: '0.5rem' }} />}
                    {uploading ? 'Uploading...' : 'Upload Document'}
                    <input type="file" hidden onChange={handleUpload} disabled={uploading} accept=".pdf,.png,.jpg,.jpeg,.txt" />
                </label>
            </div>

            <div className="card" style={{ marginBottom: '2rem' }}>
                <div className="input-group" style={{ marginBottom: 0, display: 'flex', alignItems: 'center' }}>
                    <Search style={{ color: 'var(--text-muted)', marginRight: '0.5rem' }} />
                    <input
                        type="text"
                        placeholder="Search documents..."
                        className="input-field"
                        style={{ border: 'none', background: 'transparent', padding: '0.5rem' }}
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                </div>
            </div>

            {loading ? (
                <div style={{ textAlign: 'center', padding: '2rem' }}>Loading...</div>
            ) : (
                <div style={{ display: 'grid', gap: '1rem', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))' }}>
                    {filteredDocs.map(doc => (
                        <div key={doc.id} className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem', marginBottom: '1rem' }}>
                                <div style={{ padding: '0.75rem', background: 'rgba(59, 130, 246, 0.1)', borderRadius: '0.5rem', color: 'var(--primary)' }}>
                                    <FileText />
                                </div>
                                <div style={{ overflow: 'hidden' }}>
                                    <h3 style={{ fontSize: '1rem', marginBottom: '0.25rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{doc.filename}</h3>
                                    <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>{new Date(doc.upload_date).toLocaleDateString()}</p>
                                </div>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'flex-end', borderTop: '1px solid var(--border)', paddingTop: '1rem' }}>
                                <button
                                    onClick={() => handleDelete(doc.id)}
                                    className="btn btn-outline"
                                    style={{ padding: '0.5rem', color: 'var(--error)', borderColor: 'transparent' }}
                                >
                                    <Trash2 size={18} />
                                </button>
                            </div>
                        </div>
                    ))}
                    {filteredDocs.length === 0 && (
                        <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                            No documents found. Upload one to get started.
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default Dashboard;
