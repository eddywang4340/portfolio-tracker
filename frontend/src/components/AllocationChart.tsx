import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

interface Position {
    symbol: string;
    quantity: number;
    current_price: number | null;
    current_value: number;
    cost_basis: number;
    gain_loss: number;
    gain_loss_pct: number;
}

interface AllocationChartProps {
  positions: Position[];
}

const COLORS = [
    '#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8',
    '#82CA9D', '#FFC658', '#FF6B9D', '#8DD1E1', '#D084D0'
];


const AllocationChart = ({ positions }: AllocationChartProps) => {
    const totalValue = positions.reduce((sum, pos) => sum + pos.current_value, 0);
    const minPercentage = 1.0;
    const significantPositions: any[] = [];
    let otherTotal = 0;

    positions.forEach(pos => {
        const percentage = (pos.current_value / totalValue) * 100;
        if (percentage >= minPercentage) {
            significantPositions.push({
                name: pos.symbol,
                value: pos.current_value,
                percentage: percentage
            });
        } else {
            otherTotal += pos.current_value;
        }
    });

    if (otherTotal > 0) {
        significantPositions.push({
            name: 'Other',
            value: otherTotal,
            percentage: (otherTotal / totalValue) * 100
        });
    }

    significantPositions.sort((a, b) => b.value - a.value);

    const renderLabel = (entry: any) => {
       const percentage = entry.percentage;
        if (percentage > 1) {
            return `${entry.name} (${percentage.toFixed(1)}%)`;
        }
        return '';
    };

    const CustomTooltip = ({ active, payload }: any) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload;
            return (
                 <div style={{
                    backgroundColor: 'white',
                    padding: '10px',
                    border: '1px solid #ccc',
                    borderRadius: '4px',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                }}>
                    <p style={{ margin: '0 0 5px 0', fontWeight: 'bold' }}>{data.name}</p>
                    <p style={{ margin: 0, color: '#666' }}>
                        ${data.value.toFixed(2)} ({data.percentage.toFixed(2)}%)
                    </p>
                </div>
            );
        }
        return null;
    };

    const renderLegend = (value: string, entry: any) => {
        const percentage = entry.payload.percentage;
        return `${value} (${percentage.toFixed(1)}%)`;
    }

    if (significantPositions.length === 0) {
        return (
            <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
                No data available for chart
            </div>
        );
    }

    return (
        <ResponsiveContainer width="100%" height={400}>
            <PieChart>
                <Pie
                    data={significantPositions}
                    dataKey="value"
                    cx="50%"
                    cy="50%"
                    outerRadius={120}
                    label={renderLabel}
                    labelLine={false}
                    fill="#8884d8"
                >
                    {significantPositions.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                <Legend 
                    formatter={renderLegend}
                    wrapperStyle={{ paddingTop: '20px' }}
                />
            </PieChart>
        </ResponsiveContainer>
    );
};

export default AllocationChart;