import React from 'react';
import { usePageTitle } from '../hooks/usePageTitle';
import ScanUpload from '../components/scan/ScanUpload';
import Card from '../components/common/Card';
import { ShieldCheck, Cpu, HardDrive, Lock } from 'lucide-react';
import './ScanPage.css';

export default function ScanPage() {
  usePageTitle('New Scan');

  return (
    <div id="scan-page" className="scan-page">
      <div className="scan-page__header">
        <h1 className="scan-page__title">Initiate Cryptographic Scan</h1>
        <p className="scan-page__subtitle">
          Upload repository source archives or release bundles for automated algorithm identification, key length analysis, and CBOM generation.
        </p>
      </div>

      <div className="scan-page__grid">
        {/* Main Upload Box */}
        <div className="scan-page__main">
          <Card variant="glass" title="Repository Archive Intake">
            <ScanUpload />
          </Card>
        </div>

        {/* Security & Intake Boundaries Sidebar Card */}
        <div className="scan-page__sidebar">
          <Card variant="glass" title="Intake Security &amp; Privacy">
            <ul className="scan-page__feature-list">
              <li className="scan-page__feature-item">
                <ShieldCheck size={18} className="scan-page__feature-icon" />
                <div>
                  <strong>Air-Gapped Sovereign Intake</strong>
                  <p>Processing occurs entirely on local CPU. Telemetry and external egress are strictly disabled.</p>
                </div>
              </li>
              <li className="scan-page__feature-item">
                <HardDrive size={18} className="scan-page__feature-icon" />
                <div>
                  <strong>100 MB Size Limit</strong>
                  <p>Streaming memory protections block archives exceeding 100 MB to prevent resource exhaustion.</p>
                </div>
              </li>
              <li className="scan-page__feature-item">
                <Cpu size={18} className="scan-page__feature-icon" />
                <div>
                  <strong>NIST FIPS PQC Ruleset</strong>
                  <p>Evaluates assets against ML-KEM (FIPS 203), ML-DSA (FIPS 204), and SLH-DSA (FIPS 205).</p>
                </div>
              </li>
              <li className="scan-page__feature-item">
                <Lock size={18} className="scan-page__feature-icon" />
                <div>
                  <strong>Automatic Key Redaction</strong>
                  <p>Private key material and sensitive certificate parameters are sanitized and redacted from results.</p>
                </div>
              </li>
            </ul>
          </Card>
        </div>
      </div>
    </div>
  );
}
