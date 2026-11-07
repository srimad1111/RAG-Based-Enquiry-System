import { useSystem } from '../context/SystemContext';

export function useHealth() {
  const { health, systemInfo, loading, error, refreshHealth, lastChecked } = useSystem();
  return { health, systemInfo, loading, error, refreshHealth, lastChecked };
}

export default useHealth;

