import { render, screen } from '@testing-library/react';
import React from 'react';
import { describe, it, expect } from 'vitest';
import RiskFactorBreakdown from './RiskFactorBreakdown';

describe('RiskFactorBreakdown', () => {
  const mockFactors = {
    algorithm_vulnerability: 43.5,
    mosca_horizon_urgency: 23.8,
    operational_exposure: 18.7,
    business_criticality: 14.0,
  };

  it('renders all 4 factor progress bars and labels when factors prop is provided', () => {
    render(<RiskFactorBreakdown factors={mockFactors} />);

    expect(screen.getByText('Algorithm Vulnerability')).toBeInTheDocument();
    expect(screen.getByText('Mosca Horizon Urgency')).toBeInTheDocument();
    expect(screen.getByText('Operational Exposure')).toBeInTheDocument();
    expect(screen.getByText('Business Criticality')).toBeInTheDocument();

    expect(screen.getByText('43.5%')).toBeInTheDocument();
    expect(screen.getByText('23.8%')).toBeInTheDocument();
    expect(screen.getByText('18.7%')).toBeInTheDocument();
    expect(screen.getByText('14.0%')).toBeInTheDocument();
  });

  it('computes average factors when passed riskEvaluations array', () => {
    const mockEvaluations = [
      {
        factor_contributions: {
          algorithm_vulnerability: 40.0,
          mosca_horizon_urgency: 20.0,
          operational_exposure: 20.0,
          business_criticality: 20.0,
        },
      },
      {
        factor_contributions: {
          algorithm_vulnerability: 50.0,
          mosca_horizon_urgency: 30.0,
          operational_exposure: 10.0,
          business_criticality: 10.0,
        },
      },
    ];

    render(<RiskFactorBreakdown riskEvaluations={mockEvaluations} />);

    // Average algorithm_vulnerability: 45.0%
    expect(screen.getByText('45.0%')).toBeInTheDocument();
    // Average mosca_horizon_urgency: 25.0%
    expect(screen.getByText('25.0%')).toBeInTheDocument();
  });

  it('renders empty message when no factor data is available', () => {
    render(<RiskFactorBreakdown factors={null} riskEvaluations={[]} />);

    expect(screen.getByTestId('factor-breakdown-empty')).toBeInTheDocument();
    expect(
      screen.getByText(/Factor contribution breakdown is unavailable/i)
    ).toBeInTheDocument();
  });
});
