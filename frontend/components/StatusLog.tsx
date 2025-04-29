interface Props {
	logs: string[];
  }
  
  export default function StatusLog({ logs }: Props) {
	return (
	  <div className="bg-gray-800 p-4 mt-6 rounded border border-gray-700">
		<h2 className="font-bold mb-2 text-lg text-white">Execution Log</h2>
		<ul className="text-sm text-gray-300 space-y-1">
		  {logs.map((log, index) => (
			<li key={index}>• {log}</li>
		  ))}
		</ul>
	  </div>
	);
  }
  