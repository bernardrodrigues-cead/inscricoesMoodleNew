tailwind.config = {
    theme: {
        extend: {
            colors: {
                redCead: '#ae1f25',
                yellowCead: '#fdb913',
                eigengrau: '#16161d'
            },
            fontFamily: {
                roboto: "'Roboto', sans-serif"
            },
            keyframes: {
                appearFromLeft: {
                    '0%': { 
                        opacity: 0,
                        transform: 'translateX(-50%)'
                    },
                    '10%': {
                        opacity: 1,
                        transform: 'translateX(0)'
                    },
                    '100%': {
                        opacity: 0
                    }
                }
            },
            animation: {
                'appearFromLeft': 'appearFromLeft 10s linear forwards'
            },
            filter: {
                blackToCead: 'invert(13%) sepia(84%) saturate(5202%) hue-rotate(351deg) brightness(76%) contrast(83%)'
            }
        }
    }
}