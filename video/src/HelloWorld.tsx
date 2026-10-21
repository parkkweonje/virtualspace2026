import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';

export const HelloWorld: React.FC<{title: string}> = ({title}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const scale = spring({frame, fps});
  const opacity = interpolate(frame, [0, 20], [0, 1], {extrapolateRight: 'clamp'});

  return (
    <AbsoluteFill style={{backgroundColor: '#0f172a', justifyContent: 'center', alignItems: 'center'}}>
      <h1 style={{color: 'white', fontSize: 100, fontFamily: 'sans-serif', transform: `scale(${scale})`, opacity}}>
        {title}
      </h1>
    </AbsoluteFill>
  );
};
