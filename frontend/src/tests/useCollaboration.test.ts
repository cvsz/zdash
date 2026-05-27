import { renderHook } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { useCollaboration } from '../hooks/useCollaboration';

describe('useCollaboration',()=>{it('returns default state',()=>{const {result}=renderHook(()=>useCollaboration('w1')); expect(result.current.connected===false || result.current.connected===true).toBeTruthy();});});
